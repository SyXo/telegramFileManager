import configparser

from backend.sessionsHandler import SessionsHandler
from ui.userInterface import UserInterface

def main():
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

    sHandler = SessionHandler(cfg['telegram']['channel_id'], cfg['telegram']['api_id'],
                              cfg['telegram']['api_hash'], cfg['paths']['data_path'],
                              cfg['paths']['tmp_path'], int(cfg['telegram']['max_sessions']))

    ui = UserInterface()


if __name__ == "__main__":
    main()
