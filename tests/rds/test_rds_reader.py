import os

from textcavator_readers.readers.rds import RDSReader
from textcavator_readers.readers.core import Field
from textcavator_readers.extract import Constant, CSV

class HamletReader(RDSReader):
    data_directory = os.path.dirname(__file__) + '/data'

    def sources(self):
        for filename in os.listdir(self.data_directory):
            yield os.path.join(self.data_directory, filename)

    fields = [
        Field(
            name='play',
            extractor=Constant('Hamlet'),
        ),
        Field(
            name='character',
            extractor=CSV('character')
        ),
        Field(
            name='line',
            extractor=CSV('line')
        ),
    ]

def test_rds_reader():
    reader = HamletReader()
    docs = list(reader.documents())
    assert len(docs) == 11
    assert docs[1] == {
        'play': 'Hamlet',
        'character': 'HAMLET',
        'line': 'Whither wilt thou lead me? Speak, I\'ll go no further.',
    }
