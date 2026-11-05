'''
This module contains utility classes to convert XML/HTML elements to the desired value.

Each constructor in this module creates a callable that takes an XML tag object as 
input and returns a value. These are designed to be used as the `extract` input to the
`XML` extractor. (But could be used outside of it too.)
'''

import re
import html

import bs4


class Attribute:
    '''
    Extract an attribute from the element.
    
    Will return `None` if the attribute is not present. Using `'name'` as the attribute
    will return the name of the element.
    '''
    def __init__(self, attribute: str):
        self.attribute = attribute

    def __call__(self, element: bs4.element.Tag):
        if isinstance(element, bs4.element.Tag):
            if self.attribute == 'name':
                return element.name
            return element.attrs.get(self.attribute)


class Flatten:
    '''
    Extracts the text from the element and its children, flattening the XML structure.

    The result collapses indents and is usually a decent conversion to flat text. For
    detailed control, it is usually better to write a custom function.
    '''

    def __call__(self, element: bs4.element.Tag):
        text = element.get_text()
        _softbreak = re.compile(r'(?<=\S)\n(?=\S)| +')
        _newlines = re.compile('\n+')
        _tabs = re.compile('\t+')

        return html.unescape(
            _newlines.sub(
                '\n',
                _softbreak.sub(' ', _tabs.sub('', text))
            ).strip()
        )


class Noop:
    '''
    Returns the BeautifulSoup object representing the element as-is.

    This is especially useful if you want to combine multiple XML extractors and get
    the raw data from each.
    '''
    
    def __call__(self, element: bs4.element.Tag):
        return element


class String:
    '''
    Returns the string content of the element.
    '''
    def __call__(self, element: bs4.element.Tag):
        return element.string

