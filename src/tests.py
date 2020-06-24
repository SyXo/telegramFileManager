# THIS SCRIPT SHOULD BE EXECUTED ONLY BY THE MAKEFILE

# !!! dont run this on a channel that you have other files on, it will delete
# them !!!

from os import path
from backend.transferHandler import TransferHandler
import sys
import config as cfg

data_path = ".."
tmp_path = path.expanduser("~/.tmp")
telegram_channel_id = "me"
resumeTest = 0
toResume = True

if len(sys.argv) > 1:
    if sys.argv[1] == "resume1":
        resumeTest = 1
    elif sys.argv[1] == "resume2":
        resumeTest = 2

tmp_file = path.join(tmp_path, "tfilemgr", "rand")

def printProgress(current, total, current_chunk, total_chunks, sFile):
    global toResume
    prg=int(((current/total/total_chunks)+(current_chunk/total_chunks))*100)
    print("Progress of {}: {:3d}%".format(sFile, prg), end="\r", flush=True)
    if resumeTest and toResume and prg == 50:
        print("\nTest Resume")
        toResume = False
        tg.stop(resumeTest)


def fileDataFun(fileData, sFile):
    global progressDownload
    global progressUpload
    global index

    print(fileData)

    if fileData['type'] == 1:
        progressUpload = fileData.copy()
    else:
        progressDownload = fileData.copy()

tg = TransferHandler(telegram_channel_id, cfg.api_id, cfg.api_hash,
                             data_path,tmp_path,"1",printProgress,fileDataFun,
                             local_library=False)

print("Starting uploading of file")

# Do first time uploading and resuming upload in same function

inputFileData = {'rPath'      : "temp/tfilemk_rand".split('/'),
                 'path'       : tmp_file,
                 'size'       : path.getsize(tmp_file),
                 'fileID'     : [],
                 'index'      : 1,
                 'chunkIndex' : 0,
                 'type'       : 1}

outData = tg.uploadFiles(inputFileData)
if resumeTest:
    outData = tg.uploadFiles(progressUpload)

downloadData = {'rPath'   : outData['fileData']['rPath'],
                'fileID'  : outData['fileData']['fileID'],
                'IDindex' : 0,
                'size'    : outData['fileData']['size'],
                'type'    : 2}

toResume = True
print(outData)
print("Starting downloading of file")
tg.downloadFiles(downloadData)
if resumeTest:
    tg.downloadFiles(progressDownload)

print("Deleting temp files from telegram")
if input("this is very dangerous to run, make sure the telegram channel doesn't contain any other files, if you are sure type yes: ") == 'yes':
    tg.deleteUseless([0])

tg.endSession()
