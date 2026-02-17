# Combining multiple readers

It's common for dataset to include multiple data formats, where it's useful to combine different `Reader` classes. This is necessary when you're reading multiple file formats, e.g. CSV and XML. It can also make sense when your data uses the same file format, but different data formats. (For example, CSV files with completely different column names.)

In our experience, these are the most common scenarios:

1. You need to concatenate the output from multiple readers.
2. You need one reader to parse an index file, which gives you the filenames for the content files. The content data is in another format, so this requires another reader.
3. You want to iterate through a dataset with one reader, but cross-reference it with another dataset to fill in some fields. (Effectively doing a table join.)

These are very different scenarios, so we will go over each below.

## Concatenating documents

In this scenario, different portions of your data use a different format. You can write a reader for each portion, and then create a reader that will iterate through each of these in turn.

For example, you could work with a dataset where you have one dataset that provides XML data up to a certain data, and another dataset that provides CSV data for a more recent timeframe. Neither of these source datasets covers the entire period you're interested in, but you can combine the outputs from both.

For this scenario, we provide the `ConcatReader` class. After you have created a reader for each portion of your data, you can create a `ConcatReader`, which will concatenate their outputs. This will look something like this:

```python
from ianalyzer_readers.readers.xml import XMLReader
from ianalyzer_readers.readers.csv import CSVReader
from ianalyzer_readers.readers.combined import ConcatReader
from ianalyzer_readers.readers.core import Fields
from ianalyzer_readers.extract import XML, CSV

class MyXMLReader(XMLReader):
    # reader implementation...
    fields = [
        Field('foo', extractor=XML(...)),
        Field('bar', extractor=XML(...)),
    ]

class MyCSVReader(CSVReader):
    # reader implementation...
    fields = [
        Field('foo', extractor=CSV(...)),
        Field('baz', extractor=CSV(...)),
    ]

class MyConcatReader(ConcatReader):
    reader_classes = [MyXMLReader, MyCSVReader]
    fields = [
        Field('foo'),
        Field('bar'),
        Field('baz'),
    ]
```

`MyConcatReader` will automatically iterate through the XML files, followed by the CSV files.

Some notes:
- As in the example above, it's okay if the subreaders do not implement every field from the combined reader.
- The combined reader does not check for overlap between documents, so make sure that the subreaders are not reading overlapping data.

## Using an index reader and a content reader

In this scenario, you have one file format that provides an index of the data. For example, a CSV file that contains a list of XML files, and some metadata for each. You can create a reader class to parse the index file (in this case, the CSV), and then another reader to parse the content files (in this case, the XMLs).

At present, we do not provide a helper class for this, but the logic to combine readers like this is usually straightforward. It consists of the following:

- Create a reader for your index data
- Create a reader for your content data which initialises the index reader.
- In the content reader, the `sources()` function should iterate over the `documents()` output from the index reader.
- You can pass on field values from the index reader as metadata for the content reader.

Here is an example of what this might look like:

```python
from ianalyzer_readers.readers.xml import XMLReader
from ianalyzer_readers.readers.csv import CSVReader
from ianalyzer_readers.readers.core import Fields
from ianalyzer_readers.extract import XML, CSV
from ianalyzer_readers.xml_tag import Tag, CurrentTag

class IndexReader(CSVReader):
    def sources(self, **kwargs):
        yield 'data.csv'
    
    fields = [
        Field('filename', CSV('file')),
        Field('publication', CSV('pub')),
        Field('date', CSV('date')),
    ]

class ContentReader(XMLReader):
    def __init__(self):
        self.index_reader = IndexReader()

    def sources(self, **kwargs):
        for doc in self.index_reader.sources(**kwargs):
            filename = doc['filename']
            yield filename, doc # provide doc values as metadata
    
    tag_entry = Tag('article')

    fields = [
        # fields passed on from index reader
        Field('publication', Metadata('publication')),
        Field('date', Metadata('date')),
        # fields from XML data
        Field('title', XML(Tag('title'))),
        Field('author', XML(Tag('by'))),
        Field('content', XML(Tag('content'))),
    ]
```

## Cross-referencing documents

In this scenario, you want to iterate through one dataset, but cross-reference it with values from another dataset. For example, you have one dataset with books that includes an ID for each author, and another dataset that provides information about each author. We do not currently have a standardised solution for this scenario. Below are some techniques we have used in the past.

If the data is not too large, it can work to gather all author data up front (with a specialised reader) and keep it in memory. In the `sources` implementation for your books reader, include the author data in the metadata for each object, with author IDs as keys. Then a field can extract author data like so:

```python
from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.extract import Combined, XML, Metadata

Field(
    'author_name',
    Combined(
        Metadata('authors'),
        XML(attribute='author_id'),
        transform=lambda data: data[0].get(data[1]).get('name'),
    )
)
```

In this case, you could also consider writing two readers, one for your content data, and one with the author data, and using a library like `pandas` to join the output.

In some cases, you would not know the list of authors up front, and it makes more sense to look up metadata for each author (e.g. through a web API). You can write a lookup function with a cache:

```python
from functools import cache

@cache
def get_author_name(id):
    # do something...
    return 'John Doe'

Field(
    'author_name'
    XML(attribute='author_id', transform=get_author_name)
)
```

Note that neither of these methods is suitable if the amount of metadata might exceed your available memory.
