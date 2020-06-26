import curses
import misc

from backend.sessionsHandler import SessionsHandler

class UserInterface:
    def __init__(self):
        self.NAME = "Telegram File Manager"
        self.T_STR = ["Uploading:", "Downloading:"]
        self.notifBuf = ''

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
        self.scr.timeout(5000)
        self.scr.erase()
        return inputs


    def _selectFromList(self, title, prompts):
        self.scr.nodelay(False)

        MAX_PAD_X = 250
        promptCount = len(prompts)
        scrPad = curses.newpad(promptCount+10, MAX_PAD_X) # Y, X max size
        selected = showX = showY = 0
        inputKey = None
        didQuit = False

        while inputKey != ord('\n'): # Enter
            scrPad.addstr(0, 0, title, curses.A_STANDOUT)

            for i in range(promptCount):
                scrPad.addstr(2 + i, 2, prompts[i]['title'],
                              curses.A_STANDOUT if selected == i else curses.A_NORMAL)

            tlX, tlY = os.get_terminal_size(0)
            self.scr.refresh()
            scrPad.refresh(showY, showX, 0, 0, tlY-1, tlX-1)

            inputKey = self.scr.getch()

            if inputKey == curses.KEY_DOWN and selected < promptCount-1:
                selected += 1
                if selected + 4 > showY + tlY:
                    showY += 1

            elif inputKey == curses.KEY_UP and selected > 0:
                selected -= 1
                if selected < showY:
                    showY -= 1

            elif inputKey == curses.KEY_NPAGE: # Page Down
                selected += tlY-1
                showY += tlY-1
                if selected > promptCount-1:
                    selected = promptCount-1
                if showY > promptCount-(tlY-5):
                    showY = promptCount-(tlY-5) 

            elif inputKey == curses.KEY_PPAGE: # Page Up
                selected -= tlY-1
                showY -= tlY-1
                if selected < 0:
                    selected = 0
                if showY < 0:
                    showY = 0

            elif inputKey == curses.KEY_RIGHT and showX < MAX_PAD_X:
                showX += round(tlX/2)
                if showX > MAX_PAD_X-1:
                    showX = MAX_PAD_X-1
            elif inputKey == curses.KEY_LEFT and showX >= 0:
                showX -= round(tlX/2)
                if showX < 0:
                    showX = 0

            elif inputKey in [ord('q'), ord('Q')]:
                didQuit = True
                break

        self.scr.nodelay(True)
        self.scr.timeout(5000)
        self.scr.erase()

        if didQuit:
            return None
        else:
            return prompts[selected]


    def resumeHandler(self):
        inDict = {}
        for sFile, info in self.sHandler.resumeData.items():
            if info: # has resume data
                inDict[sFile] = "Session {}:".format(sFile)

        resumeOpts = self._getInputs("Resume files found, choose an option for each: (1) Finish the transfer (2) Ignore for now (3) Delete resume file",
                                     inDict)

        for sFile, selected in resumeOpts.items():
            self.sHandler.resumeHandler(sFile, int(selected))


    def uploadHandler(self):
        inData = self._getInputs("Upload", {'path'  : "File Path:",
                                            'rPath' : "Relative Path:"})

        if not os.path.isfile(inData['path']):
            self.notifBuf = "There is no file with this path."
            return

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
        for i in self.sHandler.fileDatabase:
            totalSize += i['size']

            prompts.append({'title'  : "{}  {}".format(
                                '/'.join(i['rPath']),
                                misc.bytesConvert(i['size'])
                            ),
                            'rPath'  : i['rPath'],
                            'fileID' : i['fileID'],
                            'size'   : i['size']})

        inData = self._selectFromList("Select file to download - {} Total".format(
                                          misc.bytesConvert(totalSize)
                                      ), prompts)

        if inData:
            self.sHandler.transferInThread({'rPath'   : inData['rPath'],
                                            'fileID'  : inData['fileID'],
                                            'IDindex' : 0,
                                            'size'    : inData['size'],
                                            'type'    : 2})


    def main(self):
        optionDict = {'upload' : {'value' : False, 'function' : self.uploadHandler},
                      'download' : {'value' : False, 'function' : self.downloadHandler}}

        selected = 0

        try:
            self.resumeHandler()

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

                if self.notifBuf:
                    self.scr.addstr(tlY-1, 0, self.notifBuf, curses.A_STANDOUT)
                    self.notifBuf = ''

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