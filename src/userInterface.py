import curses
import misc

from backend.sessionsHandler import SessionsHandler

class UserInterface:
    def __init__(self):
        self.NAME = "Telegram File Manager"
        self.T_STR = ["Uploading:", "Downloading:"]

        self.cfg = misc.loadConfig()
        self.sHandler = SessionsHandler(
                self.cfg['telegram']['channel_id'], self.cfg['telegram']['api_id'],
                self.cfg['telegram']['api_hash'], self.cfg['paths']['data_path'],
                self.cfg['paths']['tmp_path'], int(self.cfg['telegram']['max_sessions'])
        )

        self.scr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        self.scr.keypad(True)
        self.scr.nodelay(True)
        self.scr.timeout(5000)
        # waits for 5 seconds or a key to be pressed to refresh the screen


    def _getInputs(self, title, prompts):
        self.scr.nodelay(False)
        curses.echo()
        curses.curs_set(True)

        self.scr.addstr(0, 0, title)
        i = 2
        inputs = {}
        for key, prompt in prompts.items():
            self.scr.addstr(i, 0, prompt)
            inputs[key] = self.scr.getstr(i + 1, 0).decode(encoding='utf-8')
            i+=3

        curses.curs_set(False)
        curses.noecho()
        self.scr.nodelay(True)
        self.scr.erase()
        return inputs


    def _selectFromList(self, title, prompts):


    def resumeHandler(self, resumeSessions):
        inDict = {}
        for i in resumeSessions:
            inDict[i] = "Session {}:".format(i)

        return self._getInputs("Resume files found, choose an option for each: (1) Finish the transfer (2) Ignore for now (3) Delete resume file", inDict)


    def uploadHandler(self):
        inData = self._getInputs("Upload", {'path'  : "File Path:",
                                            'rPath' : "Relative Path:"})

        self.sHandler.transferInThread({'rPath'      : inData['rPath'].split('/'),
                                        'path'       : inData['path'],
                                        'size'       : os.path.getsize(inData['path']),
                                        'fileID'     : [],
                                        'index'      : 0, # managed by transferHandler
                                        'chunkIndex' : 0,
                                        'type'       : 1})


    def downloadHandler(self):
        prompts = []
        totalSize = 0
        # Generate list dynamically
        for i in sHandler.fileDatabase:
            totalSize += i['size']

            tempPath = '/'.join(i['rPath'])
            prompts.append({'title'  : "{}  {}".format(tempPath, misc.bytesConvert(i['size'])),
                            'rPath'  : i['rPath'],
                            'fileID' : i['fileID'],
                            'size'   : i['size']})

        inData = self._selectFromList("Select file to download - {} Total".format(totalSize),
                                      prompts)


    def main(self):
        optionDict = {'upload' : {'value' : False, 'function' : self.uploadHandler},
                      'download' : {'value' : False, 'function' : self.downloadHandler}}

        selected = 0

        try:
            while True:
                self.scr.erase()
                tlX, tlY = os.get_terminal_size(0)

                for option, info in optionDict.items():
                    if info['value']:
                        info['function']()
                        info['value'] = False
                        break

                usedSessionStr = "[ {} of {} ]".format(
                    self.sHandler.max_sessions - len(self.sHandler.freeSessions), self.sHandler.max_sessions)

                # program name
                self.scr.addstr(0, max(round((tlX-len(self.NAME))/2), 0), self.NAME)
                # Nr of used sessions
                self.scr.addstr(1, max(tlX-len(usedSessionStr), 0), usedSessionStr)

                # transfer info
                i = 2 # on which line to start displaying transfers
                if selected:
                    for j in range((selected-1)*4+i, (selected-1)*4+i+3):
                        self.scr.addch(j, 0, '*')

                for sFile, info in self.sHandler.transferInfo.items():
                    if not info['type']: # empty
                        continue

                    self.scr.addstr(i, 2, self.T_STR[info['type']-1])
                    self.scr.addstr(i+1, 2, "/".join(info['rPath']))
                    self.scr.addstr(i+2, 2, "{}% - {}".format(info['progress'], misc.bytesConvert(info['size'])))
                    i+=4

                ch = self.scr.getch()
                if ch == curses.KEY_UP and selected > 1:
                    selected -= 1
                elif ch == curses.KEY_DOWN and selected < self.sHandler.max_sessions - len(self.sHandler.freeSessions):
                    selected += 1

                elif ch == ord(self.cfg['keybinds']['upload']):
                    optionDict['upload']['value'] = True
                elif ch == ord(self.cfg['keybinds']['download']):
                    optionDict['download']['value'] = True

                elif ch == 17: # Ctrl-Q
                    break

                # Go to the last transfer if the transfer that was selected finished
                if selected > self.sHandler.max_sessions - len(self.sHandler.freeSessions):
                    selected = self.sHandler.max_sessions - len(self.sHandler.freeSessions)

        except KeyboardInterrupt: # dont crash the terminal when quitting with Ctrl+C
            pass

        # exit
        curses.endwin()
        self.sHandler.endSessions() # Must call to exit the program


if __name__ == "__main__":
    ui = UserInterface()
    ui.main()