from typing import Self

class archiveFolderObject(object):
    '''
    Used to collect information on all the files in the folder

    Could hold inferred, extraced, learned attributes ect.
    '''
    def __init__(self):
        pass

    @classmethod    
    def initFromStoredObject(self, storedObjectPath:str) -> Self:
        '''
        Take the stored extracted text, images, ect to construct this class,
        instead of having it processed from input files over again 
        '''
        pass

    def saveAsObjectFile(self) -> None:
        '''
        Functionality to dump stored text ect. to a JSON file or something similar
        '''
        pass