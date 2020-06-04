import os
import curses
import configparser
import pyrCaller
import threading

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


class transferHandler:
    def __init__(self, telegram_channel_id, api_id, api_hash,
                 data_path, tmp_path, max_sessions):

        self.api_id = api_id
        self.api_hash = api_hash
        self.data_path = data_path
        self.max_sessions = max_sessions
        self.transferInfo = {}
        self.freeSessions = []
        self.tgObject = {}

        # initialize all the pyrCaller sessions that will be used
        for i in range(1, max_sessions+1):
            self.transferInfo[str(i)] = []
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


    def saveProgress(self, current, total, current_chunk, total_chunks, sFile):
        prg=int(((current/total/total_chunks)+(current_chunk/total_chunks))*100)
        self.transferInfo[sFile][2] = "{}%".format(prg)


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

        self.transferInfo[sFile] = [fileData[0][0], fileData[0][1], "0%", action]
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

selected = 0
try:
    while True:
        scr.erase()
        tlX, tlY = os.get_terminal_size(0)

        usedSessionStr = "[ {} of {} ]".format(
            tHand.max_sessions - len(tHand.freeSessions), tHand.max_sessions)

        # program name
        scr.addstr(0, max(round((tlX-len(NAME))/2), 0), NAME, curses.A_NORMAL)
        # Nr of used sessions
        scr.addstr(1, max(tlX-len(usedSessionStr), 0), usedSessionStr, curses.A_NORMAL)

        # transfer info
        i = 2
        for sessionStr, info in tHand.transferInfo.items():
            if not info: # empty
                continue

            if str(selected) == sessionStr:
                for j in range(i, i+3):
                    scr.addch(j, 0, '*')

            scr.addstr(i, 2, T_STR[info[3]-1], curses.A_NORMAL)
            scr.addstr(i+1, 2, "/".join(info[0]), curses.A_NORMAL)
            scr.addstr(i+2, 2, "{} - {}".format(info[2], bytesConvert(info[1])), curses.A_NORMAL)
            i+=4

        ch = scr.getch()
        if ch == curses.KEY_UP and selected > 1:
            selected -= 1

        elif ch == curses.KEY_DOWN and selected < tHand.max_sessions - len(tHand.freeSessions):
            selected += 1

        elif ch == ord(cfg['keybinds']['upload']):
            break

        elif ch == 17: # Ctrl+Q
            break
except KeyboardInterrupt: # dont crash the terminal when quitting with Ctrl+c
    pass

# exit
curses.endwin()