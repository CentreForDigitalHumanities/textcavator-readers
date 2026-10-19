'''
This module defines the JSONReader.

It can parse documents nested in one file or multiple files with one document each.

Uses the Python base library `json` and the utilities provided in `textcavator_readers.json_utils`
'''

import json

from .core import Reader
import textcavator_readers.extract as extract
from textcavator_readers.json_utils import JSONStep, iterate_steps

class JSONReader(Reader):
    '''
    A base class for Readers of JSON encoded data.

    The reader can either be used on a collection of JSON files in which each file
    represents a document, or for a JSON file containing lists of documents.

    Attributes:
        record_path: List of JSONStep objects that specifies the path to document entry
            points within each file. Default is `[]`, meaning the whole file
            represents a single document.
    """

    Examples:
        ### Multiple documents in one file:
        ```python
        from textcavator_readers.json_utils import Key, Root, Values

        example_data = {
            'path': {
                'sketch': 'Hungarian Phrasebook',
                'episode': 25,
                'to': {
                    'records':
                        [
                            {'speech': 'I will not buy this record. It is scratched.', 'character': 'tourist'},
                            {'speech': "No sir. This is a tobacconist's.", 'character': 'tobacconist'}
                        ]
                }
            }
        }

        MyJSONReader(JSONReader):
            record_path = [Key('path'), Key('to'), Key('records'), Values()]

            speech = Field('speech', JSON(Key('speech')))
            character = Field('character', JSON(Key('character')))
            sketch = Field('sketch', JSON(Root(), Key('path'), Key('sketch')))
            episode = Field('episode', JSON(Root(), Key('path'), Key('episode')))
            
            fields = [speech, character, sketch, episode]
        ```

        ### Single document per file:
        ```python
        example_data = {
            'sketch': 'Hungarian Phrasebook',
            'episode': 25,
            'scene': {
                'character': 'tourist',
                'speech': 'I will not buy this record. It is scratched.'
            }
        }

        MyJSONReader(JSONReader):
            speech = Field('speech', JSON(Key('scene'), Key('speech')))
            character = Field('character', JSON(Key('scene'), Key('character')))
            sketch = Field('sketch', JSON(Key('sketch')))
            episode = Field('episode', JSON(Key('episode')))

            fields = [speech, character, sketch, episode]

        ```

    '''

    record_path: list[JSONStep] = list()
    '''
    A list of steps to retrieve document entry points from the full JSON data. If
    left blank, the full object will represent a single document.
    '''

    def validate(self):
        self._reject_extractors(extract.XML, extract.CSV, extract.RDF)


    def iterate_data(self, data, metadata):
        for path in iterate_steps(data, [], self.record_path):
            yield {
                'json': data,
                'doc_path': path,
            }


    def data_from_file(self, path):
        with open(path, "r") as f:
            data = json.load(f)
        return data


    def data_from_bytes(self, bytes):
        return json.loads(bytes)
    

    def data_from_response(self, response):
        return response.json()
