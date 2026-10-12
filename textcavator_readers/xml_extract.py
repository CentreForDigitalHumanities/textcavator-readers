'''
This module contains utility classes to convert XML/HTML elements to the desired value.
'''

import re
import html

import bs4


class Attribute:
    def __init__(self, attribute: str):
        self.attribute = attribute

    def __call__(self, element: bs4.element.Tag):
        if isinstance(element, bs4.element.Tag):
            if self.attribute == 'name':
                return element.name
            return element.attrs.get(self.attribute)


class Flatten:
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
    def __call__(self, element: bs4.element.Tag):
        return element


class String:
    def __call__(self, element: bs4.element.Tag):
        return element.string

