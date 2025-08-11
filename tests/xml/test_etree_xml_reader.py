import os

from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.readers.etree import EtreeXMLReader
from ianalyzer_readers.extract import XPath
from test_xml_reader import target_documents

class HamletEtreeXMLReader(EtreeXMLReader):
    data_directory = os.path.join(os.path.dirname(__file__), 'data')
    path_entry = './content/act/scene/lines'

    def sources(self, **kwargs):
        for filename in os.listdir(self.data_directory):
            full_path = os.path.join(self.data_directory, filename)
            yield full_path


    title = Field(
        'title',
        XPath('./meta/title', toplevel=True),
    )
    character = Field(
        'character',
        XPath('.', attribute='character')
    )
    lines = Field(
        'lines',
        XPath('l', multiple=True, transform='\n'.join)
    )

    fields = [character, lines, title]

def test_etree_xml_reader():
    reader = HamletEtreeXMLReader()
    docs = reader.documents()

    for doc, target in zip(docs, target_documents):
        assert doc == target
