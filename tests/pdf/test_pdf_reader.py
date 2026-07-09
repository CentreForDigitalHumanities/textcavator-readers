import os
from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.readers.pdf import PDFReader
from ianalyzer_readers.extract import Metadata, Order, PageText

class HamletPDFReader(PDFReader):
    data_directory = os.path.join(os.path.dirname(__file__), "data")

    def sources(self, **kwargs):
         for filename in os.listdir(self.data_directory):
            full_path = os.path.join(self.data_directory, filename)
            name, _ = os.path.splitext(filename)
            yield full_path, { 'filename': name }

    fields = [
        Field(
            name='play',
            extractor=Metadata('filename'),
        ),
        Field(
            name='page',
            extractor=Order(),
        ),
        Field(
            name='content',
            extractor=PageText({'extraction_mode': 'layout'}),
        ),
    ]


_snippet = '''HAMLET.
Whither wilt thou lead me? Speak, I’ll go no further.
GHOST.
Mark me.'''


def test_pdf_reader():
    reader = HamletPDFReader()
    docs = list(reader.documents())
    assert len(docs) == 8

    content = docs[0]['content']
    print(content)
    assert _snippet in content
