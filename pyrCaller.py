'''
The files uploaded to telegram will have this naming convention:
[s_file]_[index]  example: 1_3128

The maximum filename length for a file is 64 ASCII chars (for telegram)
2 chars will be allocated for the session file part

This means that we have 10^62 filenames possible with only digits
(for each session file)

Don't upload files that are in the same directory as data_path

The path of the uploaded file should only have ASCII characters,
because the string is transmitted to a C function
'''

from ctypes import *
from pyrogram import Client
from shutil import copyfile
from os import remove, path
from time import sleep

class pyrogramFuncs:
    def __init__(self, telegram_channel_id, api_id, api_hash, data_path,
                 tmp_path, s_file, progress_fun, data_fun):

        self.extern = CDLL(path.join(data_path, "pyrCaller_extern.so"))
        self.extern.splitFile.restype = c_size_t
        self.extern.splitFile.argtypes = [c_size_t, c_char_p, c_char_p,
                                          c_size_t, c_size_t]

        self.extern.concatFiles.restype = c_char
        self.extern.concatFiles.argtypes = [c_char_p, c_char_p, c_size_t] 

        self.telegram = Client(path.join(data_path, "a{}".format(s_file)),
                               api_id, api_hash)

        self.telegram_channel_id = telegram_channel_id
        self.data_path = data_path
        self.tmp_path = tmp_path
        self.s_file = s_file # we need this for the naming when uploading
        self.progress_fun = progress_fun
        self.data_fun = data_fun
        self.now_transmitting = 0 # no, single chunk, multi chunk (0-2)
        self.should_stop = 0


    def uploadFiles(self, fileData={}):
        if (not fileData) or not (type(fileData) is dict):
            raise TypeError("Bad or empty value given.")

        if fileData['size'] <= 1572864000: # less than 1500M don't split file
            # Single chunk upload doesn't call data_fun
            copied_file_path = path.join(self.tmp_path, "tfilemgr",
                "{}_{}".format(self.s_file, fileData['index']))

            copyfile(fileData['path'], copied_file_path)

            self.now_transmitting = 1
            self.telegram.start()

            file_ID = self.telegram.send_document(
                    self.telegram_channel_id, copied_file_path,
                    progress=self.progress_fun,
                    progress_args=(0, 1, self.s_file) # 0 out of 1 chunks
                ).message_id

            self.telegram.stop()
            self.now_transmitting = 0

            # Canceling with 1 makes no sense for single chunk transmission
            if self.should_stop == 2:
                self.should_stop = 0
                return

            remove(copied_file_path) # finished uploading, delete file

            # return file information
            return {'rPath'    : fileData['rPath'],
                    'fileID'   : [file_ID], # keep as list for compatibility
                    'IDindex'  : 0,
                    'size'     : fileData['size'],
                    'resuming' : 0}

        # else file should be split
        tot_chunks = (fileData['size'] // 1572864000) + 1 # used by progress fun

        self.now_transmitting = 2
        self.telegram.start()
        while True: # not end of file
            copied_file_path = path.join(self.tmp_path, "tfilemgr",
                "{}_{}".format(self.s_file, fileData['index']))

            fileData['chunkIndex'] = self.extern.splitFile(
                fileData['chunkIndex'],
                fileData['path'].encode('ascii'),
                copied_file_path.encode('ascii'),
                1572864, 1000
            )

            msg_obj = self.telegram.send_document(
                    self.telegram_channel_id,
                    copiedFilePath,
                    progress=self.progress_fun,
                    progress_args=(len(fileData['fileID']), tot_chunk,
                                   self.s_file)
            )

            remove(copied_file_path) # delete the chunk

            if self.should_stop == 2: # force stop
                break

            fileData['fileID'].append(msgObj.message_id)

            if not fileData['chunkIndex']: # reached EOF
                break

            fileData['index'] += 1

            self.data_fun(fileData, self.s_file, 1)

            if self.should_stop == 1:
                break

        self.telegram.stop()
        self.now_transmitting = 0
        self.should_stop = 0 # Set this to 0 no matter what

        if not fileData['chunkIndex']: # finished uploading
            return {'rPath'    : fileData['rPath'],
                    'fileID'   : fileData['fileID'],
                    'IDindex'  : 0,
                    'size'     : fileData['size'],
                    'resuming' : 0}
            # return file information


    def downloadFiles(self, fileData=[]):
        if (not fileData) or not (type(fileData) is list):
            raise TypeError("Bad or empty value given.")

        if len(fileData[0][0][2]) == 1: # no chunks
            # Single chunk download doesn't call data_fun
            copiedFilePath=path.join(self.data_path,"downloads",
                                     fileData[0][0][-1])

            self.now_transmitting = 1
            self.telegram.start()

            self.telegram.get_messages(self.telegram_channel_id,
                                       fileData[0][2][0]).download(
                file_name=copiedFilePath,
                progress=self.progress_fun,
                progress_args=(0, 1, self.s_file)
            )

            self.telegram.stop()
            self.now_transmitting = 0

            if self.should_stop == 2:
                self.should_stop = 0
                return 0

            return 1

        # else has chunks
        i = fileData[1] # this is the total number of chunks

        copiedFilePath = path.join(self.tmp_path, "tfilemgr",
                                   "{}_chunk".format(fileData[0][-1]))

        self.now_transmitting = 2
        self.telegram.start()
        while i < len(fileData[0][0][2]):
            self.telegram.get_messages(self.telegram_channel_id,
                                       fileData[0][2][i]).download(
                    file_name=copiedFilePath,
                    progress=self.progress_fun,
                    progress_args=(i, len(fileData[0][0][2]), self.s_file)
            )

            if self.should_stop == 2:
                break

            i+=1

            self.extern.concatFiles(
                copiedFilePath.encode('ascii'),
                path.join(self.data_path, "downloads",
                          fileData[0][0][-1]).encode('ascii'),
                1000
            )

            remove(copiedFilePath)

            if i == len(fileData[0][0][2]):
                # finished or canceled with 1 but it was last chunk
                self.should_stop = 0 # modify this so we return 1
                break

            # stores only ids of files that haven't yet been downloaded
            self.data_fun([fileData[0], i, 2], sFile=self.s_file)

            if self.should_stop == 1:
                # issued normal cancel
                break

        self.telegram.stop()
        self.now_transmitting = 0

        if self.should_stop:
            self.should_stop = 0 # don't confuse future transfers
            return 0

        return 1


    def deleteUseless(self, IDList=[]):
        if (not IDList) or not (type(IDList) is list):
            raise TypeError("Bad or empty value given.")

        deletedList = []
        self.telegram.start()

        for tFile in self.telegram.iter_history(self.telegram_channel_id):
            if (tFile.media) and (not tFile.message_id in IDList):
                deletedList.append(tFile.message_id)

        if deletedList:
            self.telegram.delete_messages(self.telegram_channel_id,
                    deletedList)

        self.telegram.stop()

        return deletedList


    def stop(self, stop_type=0):
        #Values of stop_type:
        #1 - Wait until the current chunk download ended and appended
        #2 - Cancel downloading, will still wait for appending to finish
        if (not stop_type) or not (type(stop_type) is int):
            raise TypeError("Bad or empty value given.")
        if not stop_type in [1, 2]:
            raise IndexError("stop_type should be 1 or 2.")
        if self.now_transmitting == 1 and stop_type == 1:
            raise IndexError("stop_type can't be 1 when transmitting single chunk files.")

        self.should_stop = stop_type
        if stop_type == 2: #force stop
            self.telegram.stop_transmission()