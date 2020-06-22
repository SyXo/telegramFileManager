from operator import itemgetter
import pickle
import os
import configparser

class FileIO:
    def __init__(self, data_path, max_sessions):
        self.data_path = data_path
        self.max_sessions = max_sessions


    def updateDatabase(self, fileDatabase, newData):
        # This should be called after finishing an upload
        # Sorts the new dict into filelist
        # then updates both in memory and to file
        fileDatabase.append(newData)
        fileDatabase.sort(key=itemgetter('rPath'))
        # This could be slow, a faster alternative is bisect.insort,
        # howewer, I couldn't find a way to sort by an item in dictionary

        with open(os.path.join(self.data_path, "fileData"), 'wb') as f:
            pickle.dump(fileDatabase, f)

        return fileDatabase


    def loadDatabase(self):
        fileDatabase = []

        if os.path.isfile(os.path.join(self.data_path, "fileData")):
            with open(os.path.join(self.data_path, "fileData"), 'rb') as f:
                self.fileDatabase = pickle.load(f)

        return fileDatabase


    def saveResumeData(self, fileData, sFile):
        with open(os.path.join(self.data_path, "resume_{}".format(sFile)), 'wb') as f:
            pickle.dump(fileData, f)


    def loadResumeData(self):
        resumeData = {}

        for i in range(1, self.max_sessions+1):
            fileData = {}
            if os.path.isfile(os.path.join(self.data_path, "resume_{}".format(i))):
                with open(os.path.join(self.data_path, "resume_{}".format(i)), 'rb') as f:
                    fileData = pickle.load(f)

            resumeData[str(i)] = fileData

        return resumeData


    def delResumeData(self, sFile):
        os.remove(os.path.join(self.data_path, "resume_{}".format(sFile)))


    def loadIndexData(self, sFile):
        if os.path.isfile(os.path.join(self.data_path, "index_{}".format(sFile))):
            with open(os.path.join(self.data_path, "index_{}".format(sFile))) as f:
                return int(f.read())
        else:
            return 1


    def saveIndexData(self, sFile, index):
        with open(os.path.join(self.data_path, "index_{}".format(sFile)), 'w') as f:
            f.write(str(index))


    def loadConfig(self):
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
