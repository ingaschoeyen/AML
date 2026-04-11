import os
import shutil
from pathlib import Path

from configs.filePaths import INPUT_DATA_FOLDER, OUTPUT_DATA_FOLDER
from classes.singleArchiveFile import singleArchiveFile

class inputFolderController(object):
    input_folder_path = None
    output_folder_path = None

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

    def createAllBasicFileObjects(self) -> list:
        inputs_path = os.path.join(self.getOutputFolderPath(), "inputs")
        if not os.path.exists(inputs_path):
            raise Exception(f"The 'inputs' folder does not exist within the folder {self.getOutputFolderPath()}")
         
        for archive_file in Path(inputs_path).rglob('*'):
            archive_file_object = singleArchiveFile(inputs_path, archive_file.relative_to(inputs_path))
            print(archive_file_object.getFileType())