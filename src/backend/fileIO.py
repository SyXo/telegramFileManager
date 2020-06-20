from operator import itemgetter
import pickle

class FileIO:
    def __init__(self, data_path):
        self.data_path = data_path


    def updateDatabase(self, fileDatabase, newInfo):
        # This should be called after finishing an upload
        # Sorts the new dict into filelist
        # then updates both in memory and to file
        fileDatabase.append(newInfo)
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