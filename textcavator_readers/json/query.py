'''
Query utilities for traversing JSON trees
'''

from typing import Iterable, Union, Callable

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


def iterate_steps(doc: JSONDoc, path: PathSpec, steps: list[JSONStep]):
    if len(steps):
        next = steps[0]
        rest = steps[1:]
        for subpath in next.find_in_tree(doc, path):
            yield from iterate_steps(doc, subpath, rest)
    else:
        yield doc, path


class JSONStep:
    def find_in_tree(self, doc: JSONDoc, path: PathSpec) -> Iterable[PathSpec]:
        raise NotImplementedError('find_in_tree must be implemented in child classes')


class Key(JSONStep):
    '''
    Get a specific key from a dictionary object.

    Parameters:
        key: The key to retrieve.
    '''
    
    def __init__(self, key: str):
        self.key = key

    def find_in_tree(self, doc: JSONDoc, path: PathSpec) -> Iterable[PathSpec]:
        item = get_path(doc, path, strict=True)
        if isinstance(item, dict):
            if self.key in item:
                yield [*path, self.key]


class Index(JSONStep):
    '''
    Get an index from an array object.

    Parameters:
        index: The index to retrieve. Negative indices are also valid.
    '''
    
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
    Specify a single, non-recursive path to retrieve from a nested object. Useful for
    shorter notations.

    Parameters:
        path: Path within the JSON. If you specify multiple arguments, they are applied
            in sequence. String argumentss can also be dot-separated to denote a sequence.

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
    '''
    Get the root of the JSON document.

    Generally, this should only be used as the first step in a sequence.
    '''
    
    def find_in_tree(self, doc, path):
        return [[]]


class Parent(JSONStep):
    '''
    Get the parent of the current element.
    '''

    def find_in_tree(self, doc, path):
        if len(path):
            yield path[:-1]
        else:
            raise LookupError('Cannot get parent from root path')


class Filter(JSONStep):
    '''
    Used to filter the results of the query up to this point by a custom function.

    Parameters:
        func: A callable that returns False (or any falsy value) for objects that should
            be omitted.
    '''

    def __init__(self, func: Callable):
        self.func = func


    def find_in_tree(self, doc, path):
        item = get_path(doc, path, strict=True)
        if self.func(item):
            yield path


class Values(JSONStep):
    '''
    Used to get all values from a dictionary or list object.
    '''

    def find_in_tree(self, doc, path):
        item = get_path(doc, path, strict=True)
        if isinstance(item, list):
            for i in range(len(item)):
                yield [*path, i]
        elif isinstance(item, dict):
            for key in item:
                yield [*path, key]


class MultiValue(JSONStep):
    '''
    Iterates items if the object is a list; otherwise stays at the current path.

    This can be used for properties that may or may not have multiple values, and where
    single values are not always wrapped in an array.
    
    If the value at the given path is a list, this will iterate over the values, but if it
    is a dictionary or a primitive, it will return the current path as-is.
    '''

    def find_in_tree(self, doc, path):
        item = get_path(doc, path, strict=True)
        if isinstance(item, list):
            for i in range(len(item)):
                yield [*path, i]
        else:
            yield path

