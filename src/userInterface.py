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


    def resumeHandler(self, resumeSessions):
        inDict = {}
        for i in resumeSessions:
            inDict[i] = "Session {}:".format(i)

        return self._getInputs("Resume files found, choose an option for each: (1) Finish the transfer (2) Ignore for now (3) Delete resume file", inDict)


    def uploadHandler(self):
        return self._getInputs("Upload", {'path'  : "File Path:",
                                          'rPath' : "Relative Path:"})


    def downloadHandler(self, fileData):
        pass # TODO


    def main(self):
        downloadMenu = uploadMenu = selected = 0

        try:
            while True:
                self.scr.erase()
                tlX, tlY = os.get_terminal_size(0)

                usedSessionStr = "[ {} of {} ]".format(
                    self.sHandler.max_sessions - len(self.sHandler.freeSessions), self.sHandler.max_sessions)

                # program name
                self.scr.addstr(0, max(round((tlX-len(self.NAME))/2), 0), self.NAME, curses.A_NORMAL)
                # Nr of used sessions
                self.scr.addstr(1, max(tlX-len(usedSessionStr), 0), usedSessionStr, curses.A_NORMAL)

                # transfer info
                i = 2 # on which line to start displaying transfers
                for sFile, info in self.sHandler.transferInfo.items():
                    if not info['type']: # empty
                        continue

                    if str(selected) == sFile: # wrong
                        for j in range(i, i+3):
                            self.scr.addch(j, 0, '*')

                    self.scr.addstr(i, 2, self.T_STR[info['type']-1], curses.A_NORMAL)
                    self.scr.addstr(i+1, 2, "/".join(info['rPath']), curses.A_NORMAL)
                    self.scr.addstr(i+2, 2, "{}% - {}".format(info['progress'], bytesConvert(info['size'])),
                               curses.A_NORMAL)
                    i+=4

                ch = self.scr.getch()
                if ch == curses.KEY_UP and selected > 1:
                    selected -= 1
                elif ch == curses.KEY_DOWN and selected < self.sHandler.max_sessions - len(self.sHandler.freeSessions):
                    selected += 1

                elif ch == ord(self.cfg['keybinds']['upload']):
                    uploadMenu = 1
                elif ch == ord(self.cfg['keybinds']['download']):
                    downloadMenu = 1

                elif ch == 17: # Ctrl+Q
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