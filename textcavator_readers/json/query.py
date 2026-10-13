'''
Query utilities for traversing JSON trees
'''

from typing import Iterable, Union


Path = list[Union[str, int]]

type JSONPrimitive = Union[str, int, float, bool, None]
type JSONDict = dict[str, 'JSONDoc']
type JSONList = list['JSONDoc']
type JSONDoc = Union[JSONPrimitive, JSONDict, JSONList]

def is_primitive(doc: JSONDoc):
    return isinstance(doc, str) or \
        isinstance(doc, int) or \
        isinstance(doc, float) or \
        isinstance(doc, bool) or \
        doc is None


def get_path(doc: JSONDoc, path: Path, strict=False):
    if is_primitive(doc):
        if len(path):
            if strict:
                raise LookupError(f'Cannot use key "{path[0]}" on primitive value "{doc}"')
            return None
        else:
            return doc

    if not len(path):
        return doc

    first = path[0]
    tail = path[1:]

    if isinstance(doc, list):
        if isinstance(first, int):
            try:
                item = doc[first]
            except IndexError as e:
                if strict:
                    raise e
                else:
                    return None

            return get_path(item, tail, strict)
        else:
            if strict:
                raise LookupError(f'Invalid key type {type(first)} for list object')
            else:
                return None

    if isinstance(doc, dict):
        if isinstance(first, str):
            try:
                item = doc[first]
            except KeyError as e:
                if strict:
                    raise e
                else:
                    return None

            return get_path(item, tail, strict)
        else:
            if strict:
                raise LookupError(f'Invalid key type {type(first)} for dict object')
            else:
                return None



class JSONStep:
    def find_in_tree(self, path: Path, doc: JSONDoc) -> Iterable[Path]:
        raise NotImplementedError('find_in_tree must be implemented in child classes')


class Key(JSONStep):
    def __init__(self, key: str):
        self.key = key

    def find_in_tree(self, path: Path, doc: JSONDoc) -> Iterable[Path]:
        return super().find_in_tree(path, doc)
