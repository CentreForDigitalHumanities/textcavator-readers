import os

from textcavator_readers.readers.html import HTMLReader
from textcavator_readers.readers.core import Field
from textcavator_readers.extract import XML
from textcavator_readers.xml_tag import Tag, CurrentTag

here = os.path.abspath(os.path.dirname(__file__))

class HamletHTMLReader(HTMLReader):
    """
    Example XML reader for testing
    """

    data_directory = os.path.join(here, 'html_example')

    tag_toplevel = Tag('body')
    tag_entry = Tag('p')

    def sources(self, **kwargs):
        for filename in os.listdir(self.data_directory):
            full_path = os.path.join(self.data_directory, filename)
            yield full_path, {
                'filename': filename
            }

    title = Field(
        'title',
        XML(Tag('h1'), toplevel=True)
    )
    character = Field(
        'character',
        XML(Tag('b'))
    )
    lines = Field(
        'lines',
        XML(CurrentTag(), flatten=True),
    )

    fields = [title, character, lines]