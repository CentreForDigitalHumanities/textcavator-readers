import os

from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.readers.etree import EtreeXMLReader
from ianalyzer_readers.extract import XPath
from test_xml_reader import target_documents

class HamletEtreeXMLReader(EtreeXMLReader):
    data_directory = os.path.join(os.path.dirname(__file__), 'data')
    path_entry = '/document/content/act/scene/lines'

    def sources(self, **kwargs):
        for filename in os.listdir(self.data_directory):
            full_path = os.path.join(self.data_directory, filename)
            yield full_path


    title = Field(
        'title',
        XPath('string(/document/meta/title/text())'),
    )
    character = Field(
        'character',
        XPath('string(@character)')
    )
    lines = Field(
        'lines',
        XPath('l/text()', transform='\n'.join)
    )

    fields = [character, lines, title]

def test_etree_xml_reader():
    reader = HamletEtreeXMLReader()
    docs = reader.documents()

    for doc, target in zip(docs, target_documents, strict=True):
        assert doc == target
