import os
import curses
import configparser
import pyrCaller

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
i = 0

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

        usedSessionStr = "[ {} of {} ]".format(len(usedSessions), MAX_SESSIONS)

        scr.addstr(1, max(tlX-len(usedSessionStr), 0),
                   usedSessionStr, curses.A_NORMAL)

        scr.addstr(2, 0, str(i), curses.A_NORMAL)
        i+=1

        ch = scr.getch()
        if ch == 17: # Ctrl+Q
            break
except KeyboardInterrupt:
    pass

# exit
curses.endwin()
