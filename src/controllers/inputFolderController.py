import os
import shutil
from pathlib import Path

from configs.filePaths import INPUT_DATA_FOLDER, OUTPUT_DATA_FOLDER
from classes.singleArchiveFile import singleArchiveFile

class inputFolderController(object):
    input_folder_path = None
    output_folder_path = None
    file_objects = {}

    def __init__(self, folder_path:str) -> None:
        self._setInputFolderPath(folder_path)
        self._setOutputFolderPath(folder_path)
        self._createOutputFolder()

    def _setInputFolderPath(self, folder_path:str) -> None:
        if not os.path.exists(INPUT_DATA_FOLDER):
            raise Exception(f"The configured INPUT_DATA_FOLDER: {INPUT_DATA_FOLDER} does not exist")

        self.input_folder_path = os.path.join(INPUT_DATA_FOLDER, folder_path)

    def _setOutputFolderPath(self, folder_path:str) -> None:
        if not os.path.exists(OUTPUT_DATA_FOLDER):
            raise Exception(f"The configured OUTPUT_DATA_FOLDER: {OUTPUT_DATA_FOLDER} does not exist")

        self.output_folder_path = os.path.join(OUTPUT_DATA_FOLDER, folder_path)

    def _createOutputFolder(self) -> None:
        os.makedirs(self.output_folder_path, exist_ok=True)

    def getInputFolderPath(self) -> str:
        return self.input_folder_path
    
    def getOutputFolderPath(self) -> str:
        return self.output_folder_path
    
    def getInputsPath(self) -> str:
        inputs_path = os.path.join(self.getOutputFolderPath(), "inputs")
        if not os.path.exists(inputs_path):
            raise Exception(f"The 'inputs' folder does not exist within the folder {self.getOutputFolderPath()}")
        
        return inputs_path
    
    def getFileObjects(self) -> dict[str,singleArchiveFile]:
        return self.file_objects
    
    def foldersAreValidPaths(self) -> bool:
        return os.path.exists(self.input_folder_path) and os.path.exists(self.output_folder_path)
    
    def copyInputIntoOutputFolder(self) -> None:
        '''
        Copy from the data Input folder to the specific output folder, where the input documents
        will be placed in an 'inputs' folder
        '''

        for input_entry in Path(self.getInputFolderPath()).rglob('*'):
            relative_path = Path(input_entry.relative_to(self.getInputFolderPath()))
            target_path = Path(os.path.join(self.getOutputFolderPath(), "inputs")) / relative_path

            if input_entry.is_dir():
                target_path.mkdir(parents=True, exist_ok=True)
            else:
                if (not target_path.exists() or 
                    input_entry.stat().st_mtime > target_path.stat().st_mtime or 
                    input_entry.stat().st_size != target_path.stat().st_size):
                    
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(input_entry, target_path)

    def createStatusFiles(self) -> None:
        status_folder_path = os.path.join(self.getOutputFolderPath(), "status")

        if not os.path.exists(status_folder_path):
            os.makedirs(status_folder_path)
            os.makedirs(os.path.join(status_folder_path, "status_per_doc"))      

    def createAllBasicFileObjects(self) -> list:
        '''
        Create the new singleArchiveFile objects, put them in the controllers file_objects set and save the object 
        '''
        for archive_file in Path(self.getInputsPath()).rglob('*'):
            if Path.is_file(archive_file):
                archive_file_object = singleArchiveFile(self.getOutputFolderPath(), archive_file.relative_to(self.getInputsPath()))
                
                name_parts = [archive_file_object.getEntrySubFolder(), archive_file_object.getCollection(), archive_file_object.getFileName()]
                file_object_name = "_".join([part for part in name_parts if part is not None])
                self.file_objects[file_object_name] = archive_file_object
                
                archive_file_object.saveAsObjectFile()