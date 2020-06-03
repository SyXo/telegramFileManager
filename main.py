import os
import curses
import configparser
import pyrCaller
import threading

class transferHandler:
    def __init__(self, telegram_channel_id, api_id, api_hash,
                 data_path, tmp_path, max_sessions):

        self.api_id = api_id
        self.api_hash = api_hash
        self.data_path = data_path
        self.tmp_path = tmp_path
        self.max_sessions = max_sessions
        self.transferProgress = {}
        self.freeSessions = []
        self.tgObject = {}

        # initialize all the pyrCaller sessions that will be used
        for i in range(1, max_sessions+1):
            self.transferProgress[str(i)] = ''
            self.freeSessions.append(str(i))

            self.tgObject[str(i)] = pyrCaller.pyrogramFuncs(
                    telegram_channel_id, api_id, api_hash, data_path,
                    tmp_path, str(i), self.saveProgress, self.saveFileData
            )


    def useSession(self):
        if not len(self.freeSessions):
            raise IndexError("No free sessions.")

        retSession = self.freeSessions[0]
        self.freeSessions.pop(0)
        return retSession


    def freeSession(self, sessionStr=''):
        if (not sessionStr) or not (type(sessionStr) is str):
            raise TypeError("Bad or empty value given.")
        if not int(sessionStr) in range(1, self.max_sessions+1):
            raise IndexError("sessionStr should be between 1 and {}.".format(self.max_sessions))
        if sessionStr in self.freeSession:
            raise ValueError("Can't free a session that is already free.")

        self.freeSessions.append(sessionStr)


    def getProgress(self, sessionStr=''):
        if (not sessionStr) or not (type(sessionStr) is str):
            raise TypeError("Bad or empty value given.")
        if not int(sessionStr) in range(1, self.max_sessions+1):
            raise IndexError("sessionStr should be between 1 and {}.".format(self.max_sessions))

        return self.transferProgress[sessionStr]


    def saveProgress(self, current, total, current_chunk, total_chunks, sFile):
        prg=int(((current/total/total_chunks)+(current_chunk/total_chunks))*100)
        self.transferProgress[sFile] = "{}%".format(prg)


    def saveFileData(self, fileData, sFile):
        with open(os.path.join(self.data_path, "resume_{}".format(sFile)), 'w') as f:
            f.write(str(fileData))


    def transfer(self, fileData=[], action=0):
        # use same function for uploading and downloading as they are similar
        # action is 1 for uploading and 2 for downloading
        if (not fileData) or not (type(fileData) is list):
            raise TypeError("Bad or empty value given.")
        if (not sFile) or not (type(sFile) is str):
            raise TypeError("Bad or empty value given.")

        sFile = useSession() # Use a free session

        if action == 1:
            transferJob = threading.Thread(self.tgObject[sFile].uploadFiles,
                                           args=(fileData))
        else:
            transferJob = threading.Thread(self.tgObject[sFile].downloadFiles,
                                           args=(fileData))

        transferJob.start()

        freeSession(sFile)


cfg = configparser.ConfigParser()
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

try:
    while True:
        scr.erase()
        tlX, tlY = os.get_terminal_size(0)

        usedSessionStr = "[ {} of {} ]".format(
            tHand.max_sessions - len(tHand.freeSessions), tHand.max_sessions)

        scr.addstr(1, max(tlX-len(usedSessionStr), 0), usedSessionStr, curses.A_NORMAL)

        ch = scr.getch()
        if ch == 17: # Ctrl+Q
            break
except KeyboardInterrupt:
    pass

# exit
curses.endwin()