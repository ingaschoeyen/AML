from typing import Self, Optional
from pathlib import Path
import os
import json
from configs.statusses import processingStatus

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
    status = None

    def __init__(self, output_folder_path:str, relative_path_in_inputs_folder:str) -> None:
        self.output_folder_path = output_folder_path
        self._setStatus(processingStatus.NEW)
        self._splitPathIntoIdentifiers(relative_path_in_inputs_folder)

    @classmethod    
    def initFromStoredObject(self, storedObjectPath:str) -> Self:
        '''
        Take the stored extracted text, images, ect to construct this class,
        instead of having it processed from input files over again 
        '''
        with open(storedObjectPath, "r", encoding="UTF-8") as of:
            file_object_json = json.load(of)

            self._setEntrySubfolder(file_object_json["entrySubFolder"])
            self._setCollection(file_object_json["collection"])
            self._setFileName(file_object_json["fileName"])
            self._setFileType(file_object_json["fileType"])
            self._setStatus(file_object_json["status"])

        return self

    def _setEntrySubfolder(self, entry_subfolder:str) -> None:
        self.entrySubfolder = entry_subfolder

    def _setCollection(self, collection:str) -> None:
        self.collection = collection

    def _setFileName(self, file_name:str) -> None:
        self.fileName = file_name

    def _setFileType(self, file_type:str) -> None:
        '''
        Returns the filetype in lowercase
        '''
        self.fileType = file_type.lower()

    def _setStatus(self, status:processingStatus) -> None:
        self.status = status

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
    
    def getStatus(self) -> processingStatus:
        return self.status
    
    def getFullFilePath(self) -> str:
        file_path = os.path.join(self.output_folder_path, "inputs",
                                   self.getEntrySubFolder() or '', 
                                   self.getCollection() or '', 
                                   self.getFileName() + self.getFileType())
        
        return file_path

    def saveAsObjectFile(self) -> None:
        '''
        Functionality to dump stored text ect. to a JSON file or something similar
        '''
        output_path = os.path.join(self.output_folder_path, "output", 
                                   self.getEntrySubFolder() or '', 
                                   self.getCollection() or '', 
                                   self.getFileName())
        
        os.makedirs(output_path, exist_ok=True)

        with open(os.path.join(output_path, "fileObject.json"), "w", encoding="UTF-8") as of:
            object_as_json = {
                "entrySubfolder": self.getEntrySubFolder(),
                "collection": self.getCollection(),
                "fileName": self.getFileName(),
                "fileType": self.getFileType(),
                "status": self.getStatus()
            }

            json.dump(object_as_json, of, indent=2)