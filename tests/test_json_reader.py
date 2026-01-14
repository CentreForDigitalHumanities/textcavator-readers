from tests.json.json_reader import JSONDocumentReader, JSONMultipleDocumentReader
from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.extract import JSON

expected = [
    {
        'act': 'ACT I',
        'scene': 'SCENE I.  A desert place.',
        'stage_direction': 'Thunder and lightning. Enter three Witches\nExeunt',
        'character': 'First Witch',
        'lines': 'When shall we three meet again\nIn thunder, lightning, or in rain?',
    },
    *[{}] * 8,
    {
        'act': 'ACT I',
        'scene': 'SCENE I.  A desert place.',
        'stage_direction': 'Thunder and lightning. Enter three Witches\nExeunt',
        'character': 'ALL',
        'lines': "Fair is foul, and foul is fair:\nHover through the fog and filthy air.",
    },
]


def test_json_parse_single_document():
    reader = JSONDocumentReader()
    docs = list(reader.documents())
    assert len(docs) == 1
    assert docs[0].get('act') == 'ACT I'
    assert docs[0].get('character') == 'First Witch'
    assert docs[0].get('scene') == 'SCENE I.  A desert place.'


def test_json_parse_multiple_documents():
    '''test that JSON reader can parse multiple documents from an array in a single file'''
    reader = JSONMultipleDocumentReader()
    docs = list(reader.documents())
    assert len(docs) == len(expected)
    _assert_matches(expected[0], docs[0])
    _assert_matches(expected[-1], docs[-1])


def _assert_matches(target: dict, doc: dict):
    assert len(target.keys()) == len(doc.keys())
    for key in target.keys():
        assert doc.get(key) == target.get(key)

def test_json_no_key():
    reader = JSONDocumentReader()
    field = Field('data', extractor=JSON())
    reader.fields.append(field)
    doc = next(reader.documents())
    assert 'TITLE' in doc['data']
