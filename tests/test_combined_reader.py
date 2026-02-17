from ianalyzer_readers.readers.combined import ConcatReader
from ianalyzer_readers.readers.core import Field

from tests.json.json_reader import JSONMultipleDocumentReader as JSONShakespeareReader
from tests.csv.test_csv_reader import ShakespeareReader as CSVShakespeareReader


class CombinedShakespeareReader(ConcatReader):
    reader_classes = [CSVShakespeareReader, JSONShakespeareReader]
    fields = [
        Field(name='play'),
        Field(name='act'),
        Field(name='character'),
        Field(name='scene'),
        Field(name='lines'),
        Field(name='stage_direction'),
    ]

def test_combined_reader():
    reader = CombinedShakespeareReader()
    docs = list(reader.documents())

    subreader_1 = CSVShakespeareReader()
    subreader_1_docs = list(subreader_1.documents())
    subreader_2 = JSONShakespeareReader()
    subreader_2_docs = list(subreader_2.documents())

    assert len(docs) == len(subreader_1_docs) + len(subreader_2_docs) == 36
    assert docs[0].items() >= subreader_1_docs[0].items()
    assert len(docs[0]) == 6
    assert docs[len(subreader_1_docs)].items() >= subreader_2_docs[0].items()
