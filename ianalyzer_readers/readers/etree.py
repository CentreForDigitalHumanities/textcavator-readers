from lxml import etree

from ianalyzer_readers.readers.core import Reader
from ianalyzer_readers import extract
from requests import Response


class EtreeXMLReader(Reader):
    '''
    Alternative to the XMLReader

    - Built on lxml instead of BeautifulSoup
    - Pairs with the `XPath` extractor: queries for fields are provided as XPath
        expressions.

    Faster than the XMLReader (I think?) at the cost of feature support.
    '''

    path_entry: str
    'Path expression to select document entry points'

    def validate(self):
        self._reject_extractors(extract.XML, extract.CSV, extract.JSON, extract.RDF)


    def data_from_file(self, path):
        return etree.parse(path)


    def data_from_bytes(self, bytes):
        return etree.parse(bytes)


    def data_from_response(self, response: Response):
        return etree.XML(response.content)


    def iterate_data(self, data: etree.ElementTree, metadata):
        root = data.getroot()

        for element in root.iterfind(self.path_entry):
            yield { 'element': element }
