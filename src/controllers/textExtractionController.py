from classes.singleArchiveFile import singleArchiveFile
import pdfplumber

class textExtractionController(object):
    '''
    Utilise and intteract with text extraction modules to collect and save the relevant information from each provided file.

    It should take any single file in an archive folder and handle it accordingly
    '''
    def __init__(self, archive_file:singleArchiveFile) -> None:
        self.archive_file = archive_file

    def extractUnformattedText(self) -> dict[int,str]:
        '''
        See what the filetype is and take the correct extraction steps
        '''

        page_texts = {}
        if self.archive_file.getFileType() == '.pdf':
            pdf_object = pdfplumber.open(self.archive_file.getFullFilePath()) 
            
            for i, page in enumerate(pdf_object.pages):
                # TODO: determine if page is scan or not
                page_texts[i] = page.extract_text()

        return page_texts


    def completeTextExtraction(self) -> dict[int,str]:
        '''
        Call all text extraction methods and make choices to build the final text representation.

        returns a {page_i:page_text} dict

        TODO: do something more than just a quick pdf text extraction 
        '''

        return self.extractUnformattedText()
