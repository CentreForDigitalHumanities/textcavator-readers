from textcavator_readers.readers.xlsx import XLSXReader
from textcavator_readers.readers.core import Field
from textcavator_readers.extract import CSV
import os

here = os.path.abspath(os.path.dirname(__file__))


class HamletXLSXReader(XLSXReader):
    data_directory = os.path.join(here, 'xlsx_example')

    def sources(self, **kwargs):
        for filename in os.listdir(self.data_directory):
            full_path = os.path.join(self.data_directory, filename)
            yield full_path, {
                'filename': filename
            }

    fields = [
        Field(
            name='character',
            extractor=CSV(column='Character')
        ),
        Field(
            name='lines',
            extractor=CSV(column='Lines')
        )
    ]
