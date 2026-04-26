from typing import Self, Optional
from pathlib import Path
import os
import json
from configs.statusses import processingStatus
from configs.fileNames import SAVED_TEXT_FILE_NAME, SAVED_METADATA_FILE_NAME

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
    page_texts = None

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
            self.setPageTexts(file_object_json["page_texts"])

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
        self._setFileType(Path(path_parts[-1]).suffixes[-1])

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
    
    def setPageTexts(self, page_text_dict:dict[int,str]) -> None:
        self.page_texts = page_text_dict

    def getPageTexts(self) -> Optional[dict[int:str]]:
        return self.page_texts

    def saveAsObjectFile(self, override_existing:bool = True) -> None:
        '''
        Functionality to dump stored text ect. to a JSON file or something similar
        '''
        output_path = os.path.join(self.output_folder_path, "output", 
                                   self.getEntrySubFolder() or '', 
                                   self.getCollection() or '', 
                                   self.getFileName())
        
        if override_existing:
            os.makedirs(output_path, exist_ok=True)

            with open(os.path.join(output_path, "fileObject.json"), "w", encoding="UTF-8") as of:
                object_as_json = {
                    "entrySubfolder": self.getEntrySubFolder(),
                    "collection": self.getCollection(),
                    "fileName": self.getFileName(),
                    "fileType": self.getFileType(),
                    "status": self.getStatus(),
                    "page_texts": self.getPageTexts()
                }

                json.dump(object_as_json, of, indent=2)

    def saveSearchableRepresentation(self) -> None:
        '''
        Functionality to save this file as something that will be fed to the retrieval algorithm

        It will include the full text, extrected features, learned features

        And save in a specific file format

        TODO: do more than just saving the simple text as a .txt file and name as metaData dict, 
        specifically, also save a vector representation of the text and a metadata/learned feature dict
        '''

        ouptut_path = os.path.join(self.output_folder_path, "output", 
                                   self.getEntrySubFolder() or '', 
                                   self.getCollection() or '', 
                                   self.getFileName())

        joined_text = "\n".join([page_text for page_text in self.getPageTexts().values()])
        
        with open(os.path.join(ouptut_path, SAVED_TEXT_FILE_NAME), "w", encoding="UTF-8") as tf:
            tf.write(joined_text)

        tf.close()

        placeholder_metadata_dict = {
            "dataset": "N338",
            "dataset_entry": "338051",
            "document_path_in_entry": "/".join([self.getEntrySubFolder(), self.getCollection()]),
            "file_name": self.getFileName(),
            "file_type": self.getFileType()
        }
        with open(os.path.join(ouptut_path, SAVED_METADATA_FILE_NAME), "w", encoding="UTF-8") as mf:
            json.dump(placeholder_metadata_dict, mf, indent=2)

        mf.close()
