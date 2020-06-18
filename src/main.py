import os
import curses
import configparser
import pyrCaller
import threading
import fileSelector
import pickle
from operator import itemgetter

NAME = "Telegram File Manager"
T_STR = ["Uploading:", "Downloading:"]

def bytesConvert(rawBytes):
    if   rawBytes >= 16**10: # tbyte
        return "{} TBytes".format(round(rawBytes/16**10, 2))
    elif rawBytes >= 8**10: # gbyte
        return "{} GBytes".format(round(rawBytes/8**10, 2))
    elif rawBytes >= 4**10: # mbyte
        return "{} MBytes".format(round(rawBytes/4**10, 2))
    elif rawBytes >= 2**10: # kbyte
        return "{} KBytes".format(round(rawBytes/2**10, 2))
    else: return "{} Bytes".format(rawBytes)


def getInputs(scr, title, prompts):
    scr.nodelay(False)
    curses.echo()
    curses.curs_set(True)

    scr.addstr(0, 0, title)
    i = 2
    inputs = {}
    for key, prompt in prompts.items():
        scr.addstr(i, 0, prompt)
        inputs[key] = scr.getstr(i + 1, 0).decode(encoding='utf-8')
        # has a limit of 255 chars/input
        i+=3

    curses.curs_set(False)
    curses.noecho()
    scr.nodelay(True)
    scr.erase()
    return inputs


class transferHandler:
    def __init__(self, telegram_channel_id, api_id, api_hash,
                 data_path, tmp_path, max_sessions):

        self.api_id = api_id
        self.api_hash = api_hash
        self.data_path = data_path
        self.max_sessions = max_sessions
        self.tgObject = {}
        self.freeSessions = []
        self.resumeSessions = []
        self.fileDatabase = []
        self.transferInfo = {} # used by main fun

        # Load database
        if os.path.isfile(os.path.join(self.data_path, "fileData")):
            with open(os.path.join(self.data_path, "fileData"), 'rb') as f:
                self.fileDatabase = pickle.load(f)

        # initialize all the pyrCaller sessions that will be used
        for i in range(1, max_sessions+1):
            self.freeSessions.append(str(i))
            self.transferInfo[str(i)] = {}
            self.transferInfo[str(i)]['rPath'] = ''
            self.transferInfo[str(i)]['progress'] = 0
            self.transferInfo[str(i)]['size'] = 0
            self.transferInfo[str(i)]['type'] = 0

            self.tgObject[str(i)] = pyrCaller.pyrogramFuncs(
                    telegram_channel_id, api_id, api_hash, data_path,
                    tmp_path, str(i), self.saveProgress, self.saveFileData
            )

            # check for resume files
            if os.path.isfile(os.path.join(data_path, "resume_{}".format(i))):
                self.resumeSessions.append(str(i))


    def updateDatabase(self, newInfo):
        # This should be called after finishing an upload
        # Sorts the new dict into filelist
        # then updates both in memory and to file
        self.fileDatabase.append(newInfo)
        self.fileDatabase.sort(key=itemgetter('rPath'))
        # This could be slow, a faster alternative is bisect.insort,
        # howewer, I couldn't find a way to sort by an item in dictionary

        with open(os.path.join(self.data_path, "fileData"), 'wb') as f:
            pickle.dump(self.fileDatabase, f)


    def useSession(self):
        if not len(self.freeSessions):
            raise IndexError("No free sessions.")

        retSession = self.freeSessions[0]
        self.freeSessions.pop(0)
        return retSession


    def freeSession(self, sFile=''):
        if not int(sFile) in range(1, self.max_sessions+1):
            raise IndexError("sFile should be between 1 and {}.".format(self.max_sessions))
        if sFile in self.freeSession:
            raise ValueError("Can't free a session that is already free.")

        self.freeSessions.append(sFile)


    def saveProgress(self, current, total, current_chunk, total_chunks, sFile):
        prg = int(((current/total/total_chunks)+(current_chunk/total_chunks))*100)
        self.transferInfo[sFile]['progress'] = prg


    def saveFileData(self, fileData, sFile):
        with open(os.path.join(self.data_path, "resume_{}".format(sFile)), 'wb') as f:
            pickle.dump(fileData, f)


    def resumeHandler(self, sFile='', selected=0):
        if not sFile in self.resumeSessions:
            raise ValueError("This session doesn't have any resume info.")
        if not selected in range(1, 4):
            raise IndexError("selected should be between 1 and 3")

        if selected == 1: # Finish the transfer
            with open(os.path.join(data_path, "resume_{}".format(sFile)), 'rb') as f:
                fileData = pickle.load(f)

            if fileData['type'] == 1:
                self.upload(fileData)
            else:
                self.download(fileData)

        elif selected == 2: # Ignore for now
            self.freeSessions.remove(sFile)

        else: # delete the resume file
            os.remove(os.path.join(data_path, "resume_{}".format(sFile)))
            self.cleanTg()

        self.resumeSessions.remove(sFile)


    def cleanTg(self):
        sFile = self.useSession()

        IDlist = []
        for i in self.fileDatabase:
            for j in i['fileID']:
                IDlist.append(j)

        self.tgObject[sFile].deleteUseless(IDlist)
        self.freeSession(sFile)


    def upload(self, fileData={}):
        if (not fileData) or not (type(fileData) is dict):
            raise TypeError("Bad or empty value given.")
        if self.resumeSessions:
            raise ValueError("Resume sessions not handled, refusing to upload.")

        sFile = self.useSession() # Use a free session
        self.transferInfo[sFile]['rPath'] = fileData['rPath']
        self.transferInfo[sFile]['progress'] = 0
        self.transferInfo[sFile]['size'] = fileData['size']
        self.transferInfo[sFile]['type'] = 1

        with open(os.path.join(self.data_path, "index_{}".format(sFile)), 'r') as f:
            index = int(f.read())

        fileData['index'] = index

        finalData = self.tgObject[sFile].uploadFiles(fileData)

        os.remove(os.path.join(self.data_path, "resume_{}".format(sFile)))
        with open(os.path.join(self.data_path, "index_{}".format(sFile)), 'w') as f:
            f.write(str(finalData['index']))

        self.updateDatabase(finalData['fileData'])

        self.transferInfo[sFile]['type'] = 0 # not transferring anything
        self.freeSession(sFile)


    def download(self, fileData={}):
        if (not fileData) or not (type(fileData) is dict):
            raise TypeError("Bad or empty value given.")
        if self.resumeSessions:
            raise ValueError("Resume sessions not handled, refusing to download.")

        sFile = self.useSession() # Use a free session
        self.transferInfo[sFile]['rPath'] = fileData['rPath']
        self.transferInfo[sFile]['progress'] = 0
        self.transferInfo[sFile]['size'] = fileData['size']
        self.transferInfo[sFile]['type'] = 2

        finalData = self.tgObject[sFile].downloadFiles(fileData)

        os.remove(os.path.join(self.data_path, "resume_{}".format(sFile)))
        self.transferInfo[sFile]['type'] = 0
        self.freeSession(sFile)

        return finalData


    def endSessions(self):
        for i in range(1, self.max_sessions+1):
            self.tgObject[str(i)].endSession()


def main():
    cfg = configparser.ConfigParser()

    if not os.path.isfile(os.path.expanduser("~/.config/tgFileManager.ini")):
        print("Config file not found, user input required for first time configuration.")

        cfg['telegram'] = {}
        cfg['telegram']['api_id'] = ''
        cfg['telegram']['api_hash'] = ''
        cfg['telegram']['channel_id'] = 'me'
        cfg['telegram']['max_sessions'] = '4'
        cfg['paths'] = {}
        cfg['paths']['data_path'] = os.expanduser("~/tgFileManager")
        cfg['paths']['tmp_path'] = os.expanduser("~/.tmp/tgFileManager")
        cfg['keybinds'] = {}
        cfg['keybinds']['upload'] = 'u'
        cfg['keybinds']['download'] = 'd'
        cfg['keybinds']['resume'] = 'r'
        cfg['keybinds']['cancel'] = 'c'

        cfg['telegram']['api_id'] = input("api_id: ")
        cfg['telegram']['api_hash'] = input("api_hash: ")

        with open(os.path.expanduser("~/.config/tgFileManager.ini"), 'w') as f:
            cfg.write(f)
        print("Config file created at {}".format(os.path.expanduser("~/.config/tgFileManager.ini")))

    else:
        cfg.read(os.path.expanduser("~/.config/tgFileManager.ini"))

    tHand = transferHandler(cfg['telegram']['channel_id'], cfg['telegram']['api_id'],
                            cfg['telegram']['api_hash'], cfg['paths']['data_path'],
                            cfg['paths']['tmp_path'], int(cfg['telegram']['max_sessions']))

    # initialize the screen
    scr = curses.initscr()

    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    scr.keypad(True)
    scr.nodelay(True)
    scr.timeout(5000)
    # wait for 5 seconds or a key to be pressed to refresh the screen

    if tHand.resumeSessions:
        inDict = {}
        for i in tHand.resumeSessions:
            inDict[i] = "Session {}:".format(i)

        resumeOpts = getInputs(scr, "Resume files found, choose an option for each: (1) Finish the transfer (2) Ignore for now (3) Delete resume file", inDict)

        for sFile, selected in resumeOpts.items():
            tHand.resumeHandler(sFile, int(selected))

    downloadMenu = uploadMenu = selected = 0
    try:
        while True:
            scr.erase()
            tlX, tlY = os.get_terminal_size(0)

            if uploadMenu:
                strData = getInputs(scr, "Upload:", {'path'  : "File Path:",
                                                     'rPath' : "Relative Path:"})
                fileData = {'rPath'      : strData['rPath'].split('/'),
                            'path'       : strData['path'],
                            'size'       : os.path.getsize(strData['path']),
                            'fileID'     : [],
                            'index'      : 0, # managed by transferHandler
                            'chunkIndex' : 0,
                            'type'       : 1}

                upJob = threading.Thread(target=tHand.upload,
                                         args=({'rPath'      : strData['rPath'].split('/'),
                                                'path'       : strData['path'],
                                                'size'       : os.path.getsize(strData['path']),
                                                'fileID'     : [],
                                                'index'      : 0, # managed by transferHandler
                                                'chunkIndex' : 0,
                                                'type'       : 1},))
                upJob.start()
                uploadMenu = 0

            elif downloadMenu:
                totalSize = 0
                fancyList = []

                # Generate fancyList dynamically so new files will be shown
                # this could be slow, needs a check if the list was updated
                for i in tHand.fileDatabase:
                    totalSize += i['size'] # integer addition

                    tempPath = '/'.join(i['rPath'])
                    fancyList.append({'title'  : "{}  {}".format(tempPath, bytesConvert(i['size'])),
                                      'rPath'  : i['rPath'],
                                      'fileID' : i['fileID'],
                                      'size'   : i['size'],
                                      'type'   : 'file'})

                menu = {'title'   : "Select file to download:",
                        'type'    : 'menu',
                        'options' : fancyList}

                m = fileSelector.CursesMenu(menu, scr, len(menu['options'])+10)

                selectedFile = m.display()
                downJob = threading.Thread(target=tHand.download,
                                           args=({'rPath'   : selectedFile['rPath'],
                                                  'fileID'  : selectedFile['fileID'],
                                                  'IDindex' : 0,
                                                  'size'    : selectedFile['size'],
                                                  'type'    : 2},))
                downJob.start()

                downloadMenu = 0

            usedSessionStr = "[ {} of {} ]".format(
                tHand.max_sessions - len(tHand.freeSessions), tHand.max_sessions)

            # program name
            scr.addstr(0, max(round((tlX-len(NAME))/2), 0), NAME, curses.A_NORMAL)
            # Nr of used sessions
            scr.addstr(1, max(tlX-len(usedSessionStr), 0), usedSessionStr, curses.A_NORMAL)

            # transfer info
            i = 2
            for sFile, info in tHand.transferInfo.items():
                if not info['type']: # empty
                    continue

                if str(selected) == sFile: # wrong
                    for j in range(i, i+3):
                        scr.addch(j, 0, '*')

                scr.addstr(i, 2, T_STR[info['type']-1], curses.A_NORMAL)
                scr.addstr(i+1, 2, "/".join(info['rPath']), curses.A_NORMAL)
                scr.addstr(i+2, 2, "{}% - {}".format(info['progress'], bytesConvert(info['size'])),
                           curses.A_NORMAL)
                i+=4

            ch = scr.getch()
            if ch == curses.KEY_UP and selected > 1:
                selected -= 1
            elif ch == curses.KEY_DOWN and selected < tHand.max_sessions - len(tHand.freeSessions):
                selected += 1

            elif ch == ord(cfg['keybinds']['upload']):
                uploadMenu = 1
            elif ch == ord(cfg['keybinds']['download']):
                downloadMenu = 1

            elif ch == 17: # Ctrl+Q
                break
    except KeyboardInterrupt: # dont crash the terminal when quitting with Ctrl+c
        pass

    # exit
    curses.endwin()
    tHand.endSessions()


if __name__ == "__main__":
    main()
