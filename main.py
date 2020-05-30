import curses
import pyrCaller
import configparser
import os

cfg = configparser.ConfigParser()
cfg.read(os.path.expanduser("~/.config/tgFileManager.ini"))

'''
print("{}\n{}\n{}\n{}\n{}".format(
      cfg['telegram']['api_id'],
      cfg['telegram']['api_hash'],
      cfg['telegram']['channel_id'],
      cfg['paths']['data_path'],
      cfg['paths']['tmp_path']
))
'''

MAX_SESSIONS = int(cfg['telegram']['max_sessions'])
usedSessions = [1] # list of which sessions are used

# initialize the screen
scr = curses.initscr()

curses.noecho()
curses.cbreak()
curses.curs_set(0)
scr.keypad(1)

try:
    while True:
        scr.clear()
        tlX, tlY = os.get_terminal_size(0)

        usedSessionStr = "[ {} of {} ]".format(len(usedSessions), MAX_SESSIONS)

        scr.addstr(1, max(tlX-len(usedSessionStr), 0),
                   usedSessionStr, curses.A_NORMAL)

        ch = scr.getch()
        if ch == 17: # Ctrl+Q
            break
except KeyboardInterrupt:
    pass

# exit
scr.keypad(0)
curses.echo()
curses.nocbreak()
curses.endwin()
