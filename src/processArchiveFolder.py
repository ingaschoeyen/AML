import os
import sys

from controllers.inputFolderController import inputFolderController

'''
The script to recieve the path of a folder from which the documents are to be processed.
Along the lines of the N338 subset in mind, we expect each input folder to be a string of the form:
    N338/<Number>

where N338 lives in <Path To Data Folder>/data/

NOTE: the name (and probably location) of the data folder will be made configurable. This data folder will always act as the input


From there, the DOC and FOTO folders will be handled, along with any subfolders inside of them.

It does so by calling functions on controllers. Those controllers will have more detailed functionality defined.

Processing will consist of these four parts:

1. Document/folder placements
    -- The inputFolder controller will create folders and files for each input folder inside the processed_documents folder.
        Along that file structure information extraction can also take place via the controller.

2. Text extraction
    -- Using standard libraries / OCR models to extract document text and potentiall format it into better cohesion

3. (Learned) features / representations
    -- Expand upon just the extracted texts by trying to extract things such as coordinates or document descriptions

4. Representation
    -- Somewhat close to features of step 3, but put it in a (file) format that will be used by the search model.
        Could also include embedding         

Make sure that on error sys.exit(1) is returned. Default exit code 0 indicates succesful completion.
'''

input_folder = sys.argv[1]

try:
    inputController = inputFolderController(input_folder)

    inputController.copyInputIntoOutputFolder()

    inputController.createAllBasicFileObjects()

except Exception as e:
    print(str(e))
    sys.exit(1)
