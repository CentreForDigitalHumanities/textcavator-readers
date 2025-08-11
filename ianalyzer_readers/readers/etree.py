from lxml import etree

from ianalyzer_readers.readers.core import Reader, Field
from ianalyzer_readers import extract
from requests import Response


class EtreeXMLReader(Reader):

    path_entry: str

    def validate(self):
        # make sure the field size is as big as the system permits
        self._reject_extractors(extract.XML, extract.CSV, extract.JSON, extract.RDF)


    def data_from_file(self, path):
        return etree.parse(path)


    def data_from_bytes(self, bytes):
        return etree.parse(bytes)


    def data_from_response(self, response: Response):
        return etree.XML(response.content)


    def iterate_data(self, data: etree.ElementTree, metadata):
        root = data.getroot()

        for element in root.findall(self.path_entry):
            yield { 'element': element, 'root': root }
