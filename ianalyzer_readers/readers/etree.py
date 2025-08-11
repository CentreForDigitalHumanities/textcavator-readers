import xml.etree.ElementTree as ET

from ianalyzer_readers.readers.core import Reader, Field
from ianalyzer_readers import extract

class EtreeXMLReader(Reader):

    path_entry: str

    def validate(self):
        # make sure the field size is as big as the system permits
        self._reject_extractors(extract.XML, extract.CSV, extract.JSON, extract.RDF)
    
    def data_from_file(self, path):
        tree = ET.parse(path)
        return tree

    def iterate_data(self, data: ET.ElementTree, metadata):
        root = data.getroot()

        for element in root.findall(self.path_entry):
            yield { 'element': element, 'root': root }
