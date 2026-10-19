'''
Query utilities for traversing JSON trees
'''

from typing import Iterable, Union, Callable, Optional

type JSONPathElement = Union[str, int]
type JSONPath = list[JSONPathElement]

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


def is_valid_key(doc: JSONDoc, key: JSONPathElement):
    if isinstance(doc, list):
        return isinstance(key, int)
    if isinstance(doc, dict):
        return isinstance(key, str)
    return False


def get_path(doc: JSONDoc, path: JSONPath, strict: bool = True):
    '''
    Get the specified path from a JSON document.

    Unlike the `JSONQuery`-based queries, this is a straightforward lookup.

    Parameters:
        doc: The JSON document. This can also be a JSON-compatible primitive value (like
            an int).
        path: The path as a sequence of indices from top to bottom. Indices must be
            string (for dictionaries) or integer (for lists).
        strict: If `True`, this will raise an exception if the path is not valid. If
            `False`, invalid paths return `None`.
    
    Raises:
        LookupError: Raised if `strict` is `True` and the path is not valid. This may
            also be an inherited `IndexError` or `KeyError`, if the exception is due to
            an invalid index for a list or dict (respectively).
    '''
    if not len(path):
        return doc

    if is_primitive(doc):
        if strict:
            raise LookupError(f'Cannot use key "{path[0]}" on primitive value "{doc}"')
        return None

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


def iterate_steps(doc: JSONDoc, base_path: JSONPath, steps: list[JSONQuery]) -> Iterable[JSONPath]:
    '''
    Iterate through a JSON document based on the specified base path and query steps.

    This will:

    - Navigate to the `base_path` within the document.
    - Resolve the first query step in `steps` (if there is one).
    - Recursively apply the remaining `steps` (if there are any).
    - Return the resolved path.

    Parameters:
        doc: The JSON document.
        base_path: The initial path through the document. This should be an already
            resolved path. If empty, querying will be done from the document root.
        steps: Query steps to resolve from `base_path`. Can be empty to return only
            the base path as-is.
    
    Returns:
        A generator with resolved paths.
    '''

    if len(steps):
        next = steps[0]
        rest = steps[1:]
        for subpath in next.iterate(doc, base_path):
            yield from iterate_steps(doc, subpath, rest)
    else:
        yield base_path


class JSONQuery:
    '''
    Parent class for JSON query step constructors.

    Parameters:
        filter: Optional function to filter the results of the current query.
            This function will receive each resulting object as input and should return
            a boolean; if `True`, the path to the object will be included in the output.

    '''
    
    def __init__(self, filter: Optional[Callable] = None):
        self.filter = filter


    def find_in_tree(self, doc: JSONDoc, base_path: JSONPath) -> Iterable[JSONPath]:
        raise NotImplementedError('find_in_tree must be implemented in child classes')


    def iterate(self, doc: JSONDoc, base_path: JSONPath) -> Iterable[JSONPath]:
        results = self.find_in_tree(doc, base_path)
        if self.filter:
            for base_path in results:
                obj = get_path(doc, base_path)
                if self.filter(obj):
                    yield base_path
        else:
            yield from results


class Key(JSONQuery):
    '''
    Get a specific key from a dictionary object.


    Parameters:
        key: The key to retrieve.
        recursive: If `True`, the JSON document is search recursively to find the
            dictionary key within nested lists/dictionaries.
    
    
    If `recursive`, the object is searched recursively for any matching key. This can be
    more robust and compact, but can increase processing times and return false positives,
    so use with caution.
    
    If the key is nested within itself, only the top key is returned. Consider the
    following example:

    ```python
    {'foo': {'bar': {'bar': 'baz'}}
    ```

    Here:
    - `Key('bar')` would find nothing.
    - `Key('bar', recursive=True)` would find the path `['foo', 'bar']` but not
        `['foo', 'bar', 'bar']`.

    '''
    
    def __init__(self, key: str, recursive: bool = False, **kwargs):
        self.key = key
        self.recursive = recursive
        super().__init__(**kwargs)


    def find_in_tree(self, doc: JSONDoc, base_path: JSONPath) -> Iterable[JSONPath]:
        obj = get_path(doc, base_path)
        subpaths = self._search(obj, recursive=self.recursive)
        yield from ([*base_path, *path] for path in subpaths)


    def _search(self, doc: JSONDoc, recursive=False):
        if isinstance(doc, dict):
            for key, value in doc.items():
                if key == self.key:
                    yield [key]
                elif recursive:
                    for subpath in self._search(value, recursive):
                        yield [key, *subpath]

        if isinstance(doc, list) and recursive:
            for i, item in enumerate(doc):
                for subpath in self._search(item, recursive):
                    yield [i, *subpath]
            


class Index(JSONQuery):
    '''
    Get an index from an array object.

    Parameters:
        index: The index to retrieve. Negative indices are also valid.
    '''
    
    def __init__(self, index: int, **kwargs):
        self.index = index
        super().__init__(**kwargs)

    def find_in_tree(self, doc: JSONDoc, base_path: JSONPath) -> Iterable[JSONPath]:
        obj = get_path(doc, base_path)
        if isinstance(obj, list):
            if self.index < 0:
                index = len(obj) + self.index
            else:
                index = self.index
            if 0 <= index < len(obj):
                yield [*base_path, index]


class Path(JSONQuery):
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

    def __init__(self, *path: str | int, **kwargs):
        self.path = self._parse_path(path)
        super().__init__(**kwargs)


    def _parse_path(self, path: list[str | int]) -> JSONPath:
        parse_element = lambda step: \
            step.split('.') if isinstance(step, str) else [step]
        return [step for subpath in path for step in parse_element(subpath)]


    def find_in_tree(self, doc, base_path):
        obj = get_path(doc, base_path)
        try:
            get_path(obj, self.path)
        except LookupError:
            return []
        yield [*base_path, *self.path]


class Root(JSONQuery):
    '''
    Get the root of the JSON document.

    Generally, this should only be used as the first step in a sequence.
    '''
    
    def find_in_tree(self, doc, base_path):
        return [[]]


class Parent(JSONQuery):
    '''
    Get the parent of the current element.

    Use `level` to move up more than one step. Each dictionary or list index in the path
    constitutes a single level.

    Parameters:
        level: Specify the number of steps to move up in the path.
    
        
    Raises:
        LookupError: Raised if the specified level exceeds the number of steps in the
            path.
    '''

    def __init__(self, level: int = 1, **kwargs):
        self.level = level
        super().__init__(**kwargs)


    def find_in_tree(self, doc, base_path):
        if len(base_path) >= self.level:
            yield base_path[:-self.level]
        else:
            raise LookupError('Cannot get parent from root path')



class ParentKey(JSONQuery):
    '''
    Get an ancestor specified by a specific dictionary key.

    Parameters:
        key: The dict key to which the path should move up.

    Raises:
        LookupError: Raised if the specified key does not occur in the path.
    '''

    def __init__(self, key: str, **kwargs):
        self.key = key
        super().__init__(**kwargs)


    def find_in_tree(self, doc, base_path):
        if self.key in base_path:
            index = len(base_path) - next(i for i, value in enumerate(reversed(base_path)) if value == self.key)
            yield base_path[:index]
        else:
            raise LookupError(f'Key "{self.key}" not found in current path')



class Values(JSONQuery):
    '''
    Used to get all values from a dictionary or list object.
    '''

    def find_in_tree(self, doc, base_path):
        obj = get_path(doc, base_path)
        if isinstance(obj, list):
            for i in range(len(obj)):
                yield [*base_path, i]
        elif isinstance(obj, dict):
            for key in obj:
                yield [*base_path, key]
