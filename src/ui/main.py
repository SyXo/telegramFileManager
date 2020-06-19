import curses
import sys
import os

class CursesMenu:
    INIT = {'type' : 'init'}
    MAX_PAD_X = 250

    def __init__(self, menu_options, scr, list_len):

        self.scr = scr
        self.scr.nodelay(False)
        self.pad = curses.newpad(list_len, self.MAX_PAD_X)
        self.menu_options = menu_options
        self.selected_option = 0


    def prompt_selection(self):
        showX, showY = 0, 0

        option_count = len(self.menu_options['options'])

        inputKey = None

        while inputKey != ord('\n'): # ENTER
            self.pad.addstr(0, 0, self.menu_options['title'], curses.A_STANDOUT)

            for option in range(option_count):
                if self.selected_option == option:
                    self._draw_option(option, curses.A_STANDOUT)
                else:
                    self._draw_option(option, curses.A_NORMAL)

            tlX, tlY = os.get_terminal_size(0)
            self.pad.refresh(showY,showX, 0,0, tlY-1,tlX-1)

            inputKey = self.scr.getch()
            exitKeys = [ord('q'), ord('Q')]

            if inputKey == curses.KEY_DOWN:
                if self.selected_option < option_count-1:
                    self.selected_option += 1
                    if self.selected_option + 4 > showY + tlY:
                        showY += 1

            if inputKey == curses.KEY_UP:
                if self.selected_option > 0:
                    self.selected_option -= 1
                    if self.selected_option < showY:
                        showY -= 1


            if inputKey == curses.KEY_NPAGE: # Page Down
                self.selected_option += tlY-1
                showY += tlY-1
                if self.selected_option > option_count:
                    self.selected_option = option_count
                if showY > option_count-(tlY-5): showY = option_count-(tlY-5) 
            if inputKey == curses.KEY_PPAGE: # Page Up
                self.selected_option -= tlY-1
                showY -= tlY-1
                if self.selected_option < 0:
                    self.selected_option = 0
                if showY < 0: showY = 0

            if inputKey == curses.KEY_RIGHT and showX < self.MAX_PAD_X:
                showX += round(tlX/2)
                if showX > self.MAX_PAD_X-1: showX = self.MAX_PAD_X-1
            if inputKey == curses.KEY_LEFT and showX >= 0:
                showX -= round(tlX/2)
                if showX < 0: showX = 0


            if inputKey in exitKeys:
                self.selected_option = option_count #auto select exit and return
                break

        return self.selected_option


    def _draw_option(self, option_number, style):
        self.pad.addstr(2 + option_number,
                        2,
                        "{}".format(self.menu_options['options'][option_number]['title']),
                        style)


    def display(self):
        selected_option = self.prompt_selection()
        self.scr.nodelay(True)
        self.scr.erase()
        if selected_option < len(self.menu_options['options']):
            selected_opt = self.menu_options['options'][selected_option]
            return selected_opt
        else:
            return {'title' : 'Exit', 'type' : 'exitmenu'}


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