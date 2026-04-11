import pdfplumber
import os

def load_pdfPlumber_pdf(pdf_file_path:str) -> pdfplumber.pdf.PDF:
    pdf = pdfplumber.open(pdf_file_path)
    return pdf

# class archiveDocument(object):
#     def __init__(self, file_path:str, archive_id:str):
#         self.archive_id = archive_id
#         self._openPDF(file_path)
        
#     def _openPDF(self, file_path:str):
#         try:
#             self.pdf_object = pdfplumber.open(file_path)
#         except:
#             self.pdf_object = None
#             raise Exception('Could not open the PDF file at the provided file path')
        
#     def _getRelativeF()
