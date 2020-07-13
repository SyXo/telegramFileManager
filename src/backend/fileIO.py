from operator import itemgetter
import pickle
import os
import configparser

class FileIO:
    def __init__(self, data_path: str, tmp_path: str, max_sessions: int):
        self.data_path = data_path
        self.max_sessions = max_sessions

        for i in [data_path, tmp_path, os.path.join(data_path, "downloads"),
                  os.path.join(tmp_path, "tfilemgr")]:
            if not os.path.isdir(i):
                os.mkdir(i)


    def updateDatabase(self, fileDatabase: list):
        # This should be called after finishing an upload
        with open(os.path.join(self.data_path, "fileData"), 'wb') as f:
            pickle.dump(fileDatabase, f)


    def loadDatabase(self) -> list:
        fileDatabase = []

        if os.path.isfile(os.path.join(self.data_path, "fileData")):
            with open(os.path.join(self.data_path, "fileData"), 'rb') as f:
                fileDatabase = pickle.load(f)

        return fileDatabase


    def saveResumeData(self, fileData: dict, sFile: str):
        with open(os.path.join(self.data_path, "resume_{}".format(sFile)), 'wb') as f:
            pickle.dump(fileData, f)


    def loadResumeData(self) -> dict:
        resumeData = {}

        for i in range(1, self.max_sessions+1):
            fileData = {}
            if os.path.isfile(os.path.join(self.data_path, "resume_{}".format(i))):
                with open(os.path.join(self.data_path, "resume_{}".format(i)), 'rb') as f:
                    fileData = pickle.load(f)

                fileData['handled'] = 0
            resumeData[str(i)] = fileData

        return resumeData


    def delResumeData(self, sFile: str):
        os.remove(os.path.join(self.data_path, "resume_{}".format(sFile)))


    def loadIndexData(self, sFile: str) -> int:
        indexData = 1

        if os.path.isfile(os.path.join(self.data_path, "index_{}".format(sFile))):
            with open(os.path.join(self.data_path, "index_{}".format(sFile)), 'rb') as f:
                indexData = pickle.load(f)

        return indexData


    def saveIndexData(self, sFile: str, index: int):
        with open(os.path.join(self.data_path, "index_{}".format(sFile)), 'wb') as f:
            pickle.dump(index, f)
