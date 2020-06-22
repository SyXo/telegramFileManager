import curses
import misc

class UserInterface:
    def __init__(self, updateHandler):
        self.scr = curses.initscr()
        self.updateHandler = updateHandler

        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        scr.keypad(True)
        scr.nodelay(True)
        scr.timeout(5000)
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
