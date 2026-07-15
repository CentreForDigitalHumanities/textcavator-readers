import csv
import os

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF

from textcavator_readers.readers.rdf import get_uri_value, RDFReader
from textcavator_readers.readers.core import Field
from textcavator_readers.extract import RDF as RDFExtractor

here = os.path.abspath(os.path.dirname(__file__))

ns_character = "http://example.org/shakespeare/character"
ns_speaker = "http://example.org/shakespeare/hasSpeaker"
ns_opacity = "http://example.org/vision/hasOpacity"
ns_text = "http://example.org/shakespeare/hasText"
ns_line_id = "http://example.org/shakespeare/line"


class TestRDFReader(RDFReader):
    """
    Example XML reader for testing
    """

    data_directory = os.path.join(here, 'data')

    def document_subjects(self, graph: Graph):
        ''' get all subjects with a `hasSpeaker` predicate '''
        subjects = sorted(list(graph.subjects(URIRef(ns_speaker))))
        return subjects

    def sources(self, **kwargs):
        yield os.path.join(self.data_directory, 'hamlet.ttl')

    identifier = Field("id", RDFExtractor(transform=get_uri_value))
    character = Field(
        'character',
        RDFExtractor(
            URIRef(ns_speaker),
            transform=get_uri_value
        )
    )
    lines = Field(
        'lines',
        RDFExtractor(
            URIRef(ns_text),
            is_collection=True
        )
    )
    character_opacity = Field(
        'opacity',
        RDFExtractor(
            URIRef(ns_speaker),
            URIRef(ns_opacity)
        )
    )

    fields = [identifier, character, lines, character_opacity]


def create_test_data():
    ''' Use the example.csv file to write a document in turtle format '''
    graph = Graph()
    with open('./tests/csv_example/example.csv', 'r') as f:
        reader = csv.DictReader(f)
        character = ''
        for index, row in enumerate(reader):
            identifier = f'{ns_line_id}/hamlet-actI-scene5-{index}'
            if character != row['character']:
                character = row['character']
                graph.add((URIRef(identifier),
                           URIRef(ns_speaker), URIRef(f'{ns_character}/{character}')))
                if index > 0:
                    # remove the last rest triple, as this line starts a new utterance
                    graph.remove(rest_triple)

            graph.add((URIRef(identifier),
                       RDF.first, Literal(row['line'])))

            next_id = f'{ns_line_id}/hamlet-actI-scene5-{index+1}'
            rest_triple = (URIRef(identifier),
                           RDF.rest, URIRef(next_id))
            graph.add(rest_triple)

        graph.remove(rest_triple)
        graph.add((URIRef(f'{ns_character}/HAMLET'),
                   URIRef(ns_opacity), Literal(1.0)))
        graph.add((URIRef(f'{ns_character}/GHOST'),
                   URIRef(ns_opacity), Literal(0.3)))

        graph.serialize(destination='./tests/ttl_example/hamlet.ttl')
