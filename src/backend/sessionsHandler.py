'''
Extends transferHandler by managing the database and implementing multithreading
'''

from backend.transferHandler import TransferHandler
from backend.fileIO import FileIO
import threading
from operator import itemgetter

class SessionsHandler:
    def __init__(self, telegram_channel_id, api_id, api_hash,
                 data_path, tmp_path, max_sessions):

        self.api_id = api_id
        self.api_hash = api_hash
        self.data_path = data_path
        self.max_sessions = max_sessions
        self.fileIO = FileIO(data_path, tmp_path, max_sessions)
        self.tHandler = {}
        self.freeSessions = []
        self.transferInfo = {}
        self.fileDatabase = self.fileIO.loadDatabase()
        self.resumeData = self.fileIO.loadResumeData()

        for i in range(1, max_sessions+1):
            self.freeSessions.append(str(i)) # all sessions are free by default
            self.transferInfo[str(i)] = {}
            self.transferInfo[str(i)]['rPath'] = ''
            self.transferInfo[str(i)]['progress'] = 0
            self.transferInfo[str(i)]['size'] = 0
            self.transferInfo[str(i)]['type'] = 0

            self.tHandler[str(i)] = TransferHandler(
                    telegram_channel_id, api_id, api_hash, data_path, tmp_path,
                    str(i), self.__saveProgress, self.fileIO.saveResumeData
            ) # initialize all sessions that will be used


    def __useSession(self): # Gets the first available session
        if not self.freeSessions:
            raise IndexError("No free sessions.")

        retSession = self.freeSessions[0]
        self.freeSessions.pop(0)
        return retSession


    def __freeSession(self, sFile=''):
        if not int(sFile) in range(1, self.max_sessions+1):
            raise IndexError("sFile should be between 1 and {}.".format(self.max_sessions))
        if sFile in self.freeSessions:
            raise ValueError("Can't free a session that is already free.")

        self.freeSessions.append(sFile)


    def __saveProgress(self, current, total, current_chunk, total_chunks, sFile):
        prg = int(((current/total/total_chunks)+(current_chunk/total_chunks))*100)
        self.transferInfo[sFile]['progress'] = prg


    def resumeHandler(self, sFile='', selected=0):
        if not int(sFile) in range(1, self.max_sessions+1):
            raise IndexError("sFile should be between 1 and {}.".format(self.max_sessions))
        if not selected in range(1, 4):
            raise IndexError("selected should be between 1 and 3")

        if selected == 1: # Finish the transfer
            tmpResume = self.resumeData[sFile]
            self.resumeData[sFile] = {}
            self.transferInThread(tmpResume)

        elif selected == 2: # Ignore for now
            self.resumeData[sFile] = {} # wrong if in the future the user wants
                                        # to resume without closing the program
            self.freeSessions.remove(sFile)

        else: # delete the resume file
            self.resumeData[sFile] = {}
            self.fileIO.delResumeData(sFile)
            self.cleanTg()

        self.resumeData[sFile] = {}


    def cleanTg(self):
        sFile = self.__useSession()

        IDlist = []
        for i in self.fileDatabase:
            for j in i['fileID']:
                IDlist.append(j)

        self.tHandler[sFile].deleteUseless(IDlist)
        self.__freeSession(sFile)


    def _upload(self, fileData={}):
        sFile = self.__useSession() # Use a free session
        self.transferInfo[sFile]['rPath'] = fileData['rPath']
        self.transferInfo[sFile]['progress'] = 0
        self.transferInfo[sFile]['size'] = fileData['size']
        self.transferInfo[sFile]['type'] = 1

        fileData['index'] = self.fileIO.loadIndexData(sFile)

        finalData = self.tHandler[sFile].uploadFiles(fileData)

        if len(finalData['fileData']['fileID']) > 1: # not single chunk
            self.fileIO.delResumeData(sFile)

        self.fileIO.saveIndexData(sFile, finalData['index'])

        # This could be slow, a faster alternative is bisect.insort,
        # howewer, I couldn't find a way to sort by an item in dictionary
        self.fileDatabase.append(finalData['fileData'])
        self.fileDatabase.sort(key=itemgetter('rPath'))

        self.fileIO.updateDatabase(self.fileDatabase)

        self.transferInfo[sFile]['type'] = 0 # not transferring anything
        self.__freeSession(sFile)


    def _download(self, fileData={}):
        sFile = self.__useSession() # Use a free session
        self.transferInfo[sFile]['rPath'] = fileData['rPath']
        self.transferInfo[sFile]['progress'] = 0
        self.transferInfo[sFile]['size'] = fileData['size']
        self.transferInfo[sFile]['type'] = 2

        finalData = self.tHandler[sFile].downloadFiles(fileData)

        if len(fileData['fileID']) > 1:
            self.fileIO.delResumeData(sFile)

        self.transferInfo[sFile]['type'] = 0
        self.__freeSession(sFile)

        return finalData


    def transferInThread(self, fileData={}):
        if (not fileData) or not (type(fileData) is dict):
            raise TypeError("Bad or empty value given.")

        for sFile, info in self.resumeData.items():
            if info: # resume file exists
                raise ValueError("Resume sessions not handled, refusing to transfer.")

        if fileData['type'] == 1:
            threadTarget = self._upload
        elif fileData['type'] == 2:
            threadTarget = self._download

        transferJob = threading.Thread(target=threadTarget, args=(fileData,))
        transferJob.start()


    def endSessions(self):
        for i in range(1, self.max_sessions+1):
            self.tHandler[str(i)].endSession()
