from typing import Self, Optional
from pathlib import Path

class singleArchiveFile(object):
    '''
    used to represent a single file in an archive folder, such as:

    ../N338/338051/inputs/DOC/2016 paspoort/Datablad 338051.pdf

    From which we take and put into class variables:
        - entry_subfolder = DOC
        - collection = 2016 paspoort
        - file_name = Datablad 338051
        - file_type = pdf
    '''


    entrySubfolder = None
    collection = None
    fileName = None
    fileType = None

    def __init__(self, path_to_inputs_folder:str, relative_path_in_input_folder:str) -> None:
        self.path_to_inputs_folder = path_to_inputs_folder
        self._splitPathIntoIdentifiers(relative_path_in_input_folder)

    @classmethod    
    def initFromStoredObject(self, storedObjectPath:str) -> Self:
        '''
        Take the stored extracted text, images, ect to construct this class,
        instead of having it processed from input files over again 
        '''
        pass

    def _setEntrySubfolder(self, entry_subfolder:str) -> None:
        self.entrySubfolder = entry_subfolder

    def _setCollection(self, collection:str) -> None:
        self.collection = collection

    def _setFileName(self, file_name:str) -> None:
        self.fileName = file_name

    def _setFileType(self, file_type:str) -> None:
        self.fileType = file_type

    def _splitPathIntoIdentifiers(self, relative_path_in_input_folder:str) -> None:
        path_parts = Path(relative_path_in_input_folder).parts

        if len(path_parts) > 1:
            self._setEntrySubfolder(path_parts[0])

        if len(path_parts) > 2:
            self._setCollection("_".join(path_parts[1:-1]))

        self._setFileName(Path(path_parts[-1]).stem)
        self._setFileType("".join(Path(path_parts[-1]).suffixes))

    def getEntrySubFolder(self) -> Optional[str]:
        return self.entrySubfolder
    
    def getCollection(self) -> Optional[str]:
        return self.collection
    
    def getFileName(self) -> Optional[str]:
        return self.fileName
    
    def getFileType(self) -> Optional[str]:
        return self.fileType

    def saveAsObjectFile(self) -> None:
        '''
        Functionality to dump stored text ect. to a JSON file or something similar
        '''
        pass