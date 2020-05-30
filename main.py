import curses
import pyrCaller
import configparser
from os import path

cfg = configparser.ConfigParser()
cfg.read(path.expanduser("~/.config/tgFileManager.ini"))

print("{}\n{}\n{}\n{}\n{}".format(
      cfg['telegram']['api_id'],
      cfg['telegram']['api_hash'],
      cfg['telegram']['channel_id'],
      cfg['paths']['data_path'],
      cfg['paths']['tmp_path']
))
