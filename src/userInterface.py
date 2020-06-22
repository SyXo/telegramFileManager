import curses
import misc

from backend.sessionsHandler import SessionsHandler

class UserInterface:
    def __init__(self):
        cfg = misc.loadConfig()
        self.sHandler = SessionsHandler(
                cfg['telegram']['channel_id'], cfg['telegram']['api_id'],
                cfg['telegram']['api_hash'], cfg['paths']['data_path'],
                cfg['paths']['tmp_path'], int(cfg['telegram']['max_sessions'])
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

        return _getInputs("Resume files found, choose an option for each: (1) Finish the transfer (2) Ignore for now (3) Delete resume file", inDict)


    def uploadHandler(self):
        return _getInputs("Upload", {'path'  : "File Path:",
                                     'rPath' : "Relative Path:"})


    def downloadHandler(self, fileData):
        pass # TODO

    def main(self):


if __name__ == "__main__":
    ui = UserInterface()
    ui.main()
