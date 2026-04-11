from typing import Self

class singleArchiveFile(object):
    '''
    used to represent a single file in an archive folder, such as:

    ../N338/338051/inputs/DOC/2016 paspoort/Datablad 338051.pdf

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