'''
Query utilities for traversing JSON trees
'''

from typing import Iterable, Union

type PathElement = Union[str, int]
type PathSpec = list[PathElement]

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


def is_valid_key(doc: JSONDoc, key: PathElement):
    if isinstance(doc, list):
        return isinstance(key, int)
    if isinstance(doc, dict):
        return isinstance(key, str)
    return False


def get_path(doc: JSONDoc, path: PathSpec, strict=False):
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

    if not is_valid_key(doc, first):
        if strict:
            raise LookupError(f'Invalid key type {type(first)} for f{type(doc)} object')
        else:
            return None

    try:
        item = doc[first]
    except LookupError as e:
        if strict:
            raise e
        else:
            return None

    return get_path(item, tail, strict)



class JSONStep:
    def find_in_tree(self, doc: JSONDoc, path: PathSpec) -> Iterable[PathSpec]:
        raise NotImplementedError('find_in_tree must be implemented in child classes')


class Key(JSONStep):
    def __init__(self, key: str):
        self.key = key

    def find_in_tree(self, doc: JSONDoc, path: PathSpec) -> Iterable[PathSpec]:
        item = get_path(doc, path, strict=True)
        if isinstance(item, dict):
            if self.key in item:
                yield [*path, self.key]


class Index(JSONStep):
    def __init__(self, index: int):
        self.index = index

    def find_in_tree(self, doc: JSONDoc, path: PathSpec) -> Iterable[PathSpec]:
        item = get_path(doc, path, strict=True)
        if isinstance(item, list):
            if self.index < 0:
                index = len(item) + self.index
            else:
                index = self.index
            if 0 <= index < len(item):
                yield [*path, index]


class Path(JSONStep):
    '''
    Specify a single, non-recursive path. Useful for shorter notations.


    Parameters:
        path: Path within the JSON as one or more strings (will be applied in sequence).
            Strings can also be dot-separated to denote a sequence.

    Limitation: integer keys in dot-separated strings are not parsed as array indices.
    For example, `Path('foo.0.bar')` would not work if `0` is meant to index an array. In
    that case, use `Path('foo', 0, 'bar')`. This may be added later.
    '''

    def __init__(self, *path: str | int):
        self.path = self._parse_path(path)


    def _parse_path(self, path: list[str | int]) -> PathSpec:
        parse_element = lambda step: \
            step.split('.') if isinstance(step, str) else [step]
        return [step for subpath in path for step in parse_element(subpath)]


    def find_in_tree(self, doc, path):
        item = get_path(doc, path, strict=True)
        try:
            get_path(item, self.path, strict=True)
        except LookupError:
            return []
        yield [*path, *self.path]


class Root(JSONStep):
    def find_in_tree(self, doc, path):
        return [[]]