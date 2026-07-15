'''
Defines a `PDFReader` which is intended to extract text data from PDFs.
'''

from pypdf import PdfReader as PyPdfReader
from textcavator_readers.readers.core import Reader

class PDFReader(Reader):
    '''
    Base class for PDF text extraction. Thin wrapper for `pypdf`.
    
    Can be paired with the `PageText` extractor to get the text per page.
    '''

    def data_from_file(self, path: str) -> PyPdfReader:
        return PyPdfReader(path)

    def iterate_data(self, data: PyPdfReader, metadata):
        for page in data.pages:
            yield {'page': page}

