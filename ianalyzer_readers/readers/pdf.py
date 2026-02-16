from pypdf import PdfReader as PyPdfReader
from ianalyzer_readers.readers.core import Reader

class PDFReader(Reader):
    def data_from_file(self, path: str) -> PyPdfReader:
        return PyPdfReader(path)

    def iterate_data(self, data: PyPdfReader, metadata):
        for page in data.pages:
            yield {'page': page}

