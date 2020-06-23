import configparser
import os

def bytesConvert(rawBytes):
    if   rawBytes >= 16**10: # tbyte
        return "{} TBytes".format(round(rawBytes/16**10, 2))
    elif rawBytes >= 8**10: # gbyte
        return "{} GBytes".format(round(rawBytes/8**10, 2))
    elif rawBytes >= 4**10: # mbyte
        return "{} MBytes".format(round(rawBytes/4**10, 2))
    elif rawBytes >= 2**10: # kbyte
        return "{} KBytes".format(round(rawBytes/2**10, 2))
    else:
        return "{} Bytes".format(rawBytes)


def loadConfig():
    cfg = configparser.ConfigParser()

    if os.path.isfile(os.path.expanduser("~/.config/tgFileManager.ini")):
        cfg.read(os.path.expanduser("~/.config/tgFileManager.ini"))
    else:
        print("Config file not found, user input required for first time configuration.")
        cfg['telegram'] = {}
        cfg['telegram']['api_id'] = ''
        cfg['telegram']['api_hash'] = ''
        cfg['telegram']['channel_id'] = 'me'
        cfg['telegram']['max_sessions'] = '4'
        cfg['paths'] = {}
        cfg['paths']['data_path'] = os.expanduser("~/tgFileManager")
        cfg['paths']['tmp_path'] = os.expanduser("~/.tmp/tgFileManager")
        cfg['keybinds'] = {}
        cfg['keybinds']['upload'] = 'u'
        cfg['keybinds']['download'] = 'd'
        cfg['keybinds']['resume'] = 'r'
        cfg['keybinds']['cancel'] = 'c'
        cfg['telegram']['api_id'] = input("api_id: ")
        cfg['telegram']['api_hash'] = input("api_hash: ")
        with open(os.path.expanduser("~/.config/tgFileManager.ini"), 'w') as f:
            cfg.write(f)

    return cfg