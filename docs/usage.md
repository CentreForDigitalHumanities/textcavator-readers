# Usage

The intented use of this package is to extract information from a dataset.

## Core concepts

### Datasets

This package is designed for datasets that consist of one or more __source files__, which contain _structured_ information. For example, a dataset could be:

- a folder with XML files that all have the same structure
- an API where you can request JSON documents
- a single XLSX file with a data table in it

What is important is that you know the structure of these files, so you can describe (in Python) where to find a particular piece of information in each file.

### Documents

We assume that the intend output of your data extraction is a collection of __documents__. Each document is a simple dictionary that contains the information you extracted.

For example, you might extract the following two documents from a bibliographical dataset:

```python
[
    {
        'title': 'Pride and Prejudice',
        'author': 'Jane Austen',
        'year': 1813,
    }, {
        'title': 'Emma',
        'author': 'Jane Austen',
        'year': 1816,
    }
]
```

Depending on the file type of your source files, you may extract one document per source file, or multiple.

### Readers

A __reader__ is the Python object that can take a dataset, and process it into documents.

Readers usually custom-made for a specific dataset. They describe exactly where to find the dataset's files, how those files are structured into documents, what fields of information each document should contain, and how to get that information from the source file.

`textcavator_readers` provides base classes that will provide a lot basic functionality, so you don't have to start from scratch for each dataset.

### Fields

Documents are dictionaries that give a value for each __field__ you want to extract. In the example documents above, `title`, `author`, and `year` are the fields.

A reader class has fields attached to it. When the reader processes a document, it will extract the value for each field.

### Extractors

Each _field_ has an __extractor__: this is an object that finds the value of that field for a document.

When a reader extracts a document, it passes a lot of information on to each extractor, which uses that to find the information it needs. Not all readers pass exactly the same information. For example, the `XMLReader` passes a parsed XML that the extractor can query.

This means that _some extractors are only supported by specific readers_. The `XML` extractor can be used to query an XML tree - so an `XMLReader` can give it the information it needs, but a `CSVReader` cannot.

Other extractors are _generic_: they are supported by all readers.

Extractors may contain _other extractors_. Generic extractors often do: they are used to apply logic to extractors. For instance, the `Backup` extractor allows you to try one extractor, and provide a "backup" extractor if it doesn't return a value.

## Why use this package?

You will generally use `textcavator_readers` in places where you might also write a custom Python script to process your dataset. In some situations, that would be appropriate. We'll go over some reasons why `textcavator_readers` may be preferable in your situation.

### All readers have the same API

If you write one reader for an XML dataset, and one reader for a CSV dataset, you will write different underlying functions for each of them. The definition of the reader is going to depend on the type of data it needs to read.

However, once those readers are done, they will have the same API. For example, you can write a module that takes a reader as input, asks it to extract documents, and saves those documents in a database. That module won't need to check whether the reader is working with XML or CSV data: as far as it's concerned, all readers are the same.

### High-level interface

`textcavator_readers` uses generic libraries like `csv` and `beautifulsoup4`, but is designed for narrower set of use cases.  That means that if you're trying to do what the library is designed for, it's able to provide a more high-level interface. 
