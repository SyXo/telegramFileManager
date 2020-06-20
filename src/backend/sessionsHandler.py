'''
Extends transferHandler by managing the database and implementing multithreading
'''

import os
import configparser
import pyrCaller
import threading
import fileSelector

from transferHandler import TransferHandler
from fileIO import FileIO

class transferHandler(TransferHandler, FileIO):
    def __init__(self, telegram_channel_id, api_id, api_hash,
                 data_path, tmp_path, max_sessions):

        self.api_id = api_id
        self.api_hash = api_hash
        self.data_path = data_path
        self.max_sessions = max_sessions
        self.tgObject = {}
        self.freeSessions = []
        self.resumeSessions = []
        self.fileDatabase = []
        self.transferInfo = {} # used by main fun

        # initialize all the pyrCaller sessions that will be used
        for i in range(1, max_sessions+1):
            self.freeSessions.append(str(i))
            self.transferInfo[str(i)] = {}
            self.transferInfo[str(i)]['rPath'] = ''
            self.transferInfo[str(i)]['progress'] = 0
            self.transferInfo[str(i)]['size'] = 0
            self.transferInfo[str(i)]['type'] = 0

            self.tgObject[str(i)] = pyrCaller.pyrogramFuncs(
                    telegram_channel_id, api_id, api_hash, data_path,
                    tmp_path, str(i), self.saveProgress, self.saveFileData
            )

            # check for resume files
            if os.path.isfile(os.path.join(data_path, "resume_{}".format(i))):
                self.resumeSessions.append(str(i))


    def useSession(self):
        if not len(self.freeSessions):
            raise IndexError("No free sessions.")

        retSession = self.freeSessions[0]
        self.freeSessions.pop(0)
        return retSession


    def freeSession(self, sFile=''):
        if not int(sFile) in range(1, self.max_sessions+1):
            raise IndexError("sFile should be between 1 and {}.".format(self.max_sessions))
        if sFile in self.freeSessions:
            raise ValueError("Can't free a session that is already free.")

        self.freeSessions.append(sFile)


    def saveProgress(self, current, total, current_chunk, total_chunks, sFile):
        prg = int(((current/total/total_chunks)+(current_chunk/total_chunks))*100)
        self.transferInfo[sFile]['progress'] = prg


    def resumeHandler(self, sFile='', selected=0):
        if not sFile in self.resumeSessions:
            raise ValueError("This session doesn't have any resume info.")
        if not selected in range(1, 4):
            raise IndexError("selected should be between 1 and 3")

        if selected == 1: # Finish the transfer
            with open(os.path.join(data_path, "resume_{}".format(sFile)), 'rb') as f:
                fileData = pickle.load(f)

            if fileData['type'] == 1:
                self.upload(fileData)
            else:
                self.download(fileData)

        elif selected == 2: # Ignore for now
            self.freeSessions.remove(sFile)

        else: # delete the resume file
            os.remove(os.path.join(data_path, "resume_{}".format(sFile)))
            self.cleanTg()

        self.resumeSessions.remove(sFile)


    def cleanTg(self):
        sFile = self.useSession()

        IDlist = []
        for i in self.fileDatabase:
            for j in i['fileID']:
                IDlist.append(j)

        self.tgObject[sFile].deleteUseless(IDlist)
        self.freeSession(sFile)


    def upload(self, fileData={}):
        if (not fileData) or not (type(fileData) is dict):
            raise TypeError("Bad or empty value given.")
        if self.resumeSessions:
            raise ValueError("Resume sessions not handled, refusing to upload.")

        sFile = self.useSession() # Use a free session
        self.transferInfo[sFile]['rPath'] = fileData['rPath']
        self.transferInfo[sFile]['progress'] = 0
        self.transferInfo[sFile]['size'] = fileData['size']
        self.transferInfo[sFile]['type'] = 1

        if os.path.isfile(os.path.join(self.data_path, "index_{}".format(sFile))):
            with open(os.path.join(self.data_path, "index_{}".format(sFile)), 'r') as f:
                fileData['index'] = int(f.read())
        else:
            fileData['index'] = 1

        finalData = self.tgObject[sFile].uploadFiles(fileData)

        if len(finalData['fileData']['fileID']) > 1:
            os.remove(os.path.join(self.data_path, "resume_{}".format(sFile)))

        with open(os.path.join(self.data_path, "index_{}".format(sFile)), 'w') as f:
            f.write(str(finalData['index']))

        self.updateDatabase(finalData['fileData'])

        self.transferInfo[sFile]['type'] = 0 # not transferring anything
        self.freeSession(sFile)


    def download(self, fileData={}):
        if (not fileData) or not (type(fileData) is dict):
            raise TypeError("Bad or empty value given.")
        if self.resumeSessions:
            raise ValueError("Resume sessions not handled, refusing to download.")

        sFile = self.useSession() # Use a free session
        self.transferInfo[sFile]['rPath'] = fileData['rPath']
        self.transferInfo[sFile]['progress'] = 0
        self.transferInfo[sFile]['size'] = fileData['size']
        self.transferInfo[sFile]['type'] = 2

        finalData = self.tgObject[sFile].downloadFiles(fileData)

        if len(fileData['fileID']) > 1:
            os.remove(os.path.join(self.data_path, "resume_{}".format(sFile)))
        self.transferInfo[sFile]['type'] = 0
        self.freeSession(sFile)

        return finalData


    def endSessions(self):
        for i in range(1, self.max_sessions+1):
            self.tgObject[str(i)].endSession()