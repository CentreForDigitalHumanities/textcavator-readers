import pytest
from rdflib import URIRef

from .rdf_reader import TestRDFReader, get_uri_value

target_documents = [
    {
        'id': 'hamlet-actI-scene5-0',
        'character': 'HAMLET',
        'lines': ["Whither wilt thou lead me? Speak, I\'ll go no further."],
        'opacity': 1.0
    },
    {
        'id': 'hamlet-actI-scene5-1',
        'character': 'GHOST',
        'lines': ["Mark me."],
        'opacity': 0.3
    },
    {
        'id': 'hamlet-actI-scene5-2',
        'character': 'HAMLET',
        'lines': ["I will."],
        'opacity': 1.0
    },
    {
        'id': 'hamlet-actI-scene5-3',
        'character': 'GHOST',
        'lines': [
            "My hour is almost come,",
            "When I to sulph\'rous and tormenting flames",
            "Must render up myself."
        ],
        'opacity': 0.3
    },
    {
        'id': 'hamlet-actI-scene5-6',
        'character': 'HAMLET',
        'lines': ["Alas, poor ghost!"],
        'opacity': 1.0,
    },
    {
        'id': 'hamlet-actI-scene5-7',
        'character': 'GHOST',
        'lines': [
            "Pity me not, but lend thy serious hearing",
            "To what I shall unfold."
        ],
        'opacity': 0.3
    },
    {
        'id': 'hamlet-actI-scene5-9',
        'character': 'HAMLET',
        'lines': ["Speak, I am bound to hear."],
        'opacity': 1.0
    },
]


def test_rdf_number_documents():
    reader = TestRDFReader()
    docs = reader.documents()
    assert len(list(docs)) == 7


def test_rdf_document_content():
    reader = TestRDFReader()
    docs = reader.documents()
    for doc, target in zip(docs, target_documents):
        assert len(target.keys()) == len(doc.keys())
        for key in target.keys():
            assert doc.get(key) == target.get(key)


def test_get_node_value():
    input = URIRef("https://purl.org/mynamespace#ernie")
    assert get_uri_value(input) == "ernie"
    input = URIRef("https://purl.org/mynamespace/ernie")
    assert get_uri_value(input) == "ernie"
