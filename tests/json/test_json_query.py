import pytest
from textcavator_readers.json.query import (
    is_primitive, get_path, Key, Index
)

def test_is_primitive():
    assert is_primitive('test')
    assert is_primitive(1)
    assert is_primitive(.01)
    assert is_primitive(False)
    assert is_primitive(None)
    assert not is_primitive([])
    assert not is_primitive(['test'])
    assert not is_primitive({'test': 1})


path_cases = [
    ('foo', ['bar'], None, True),
    ('foo', [], 'foo', False),
    (None, [], None, False),
    (['foo', 'bar'], [0], 'foo', False),
    (['foo', 'bar'], [1], 'bar', False),
    (['foo', 'bar'], [2], None, True),
    (['foo', 'bar'], [], ['foo', 'bar'], False),
    ({'foo': 'bar'}, ['foo'], 'bar', False),
    ({'foo': 'bar'}, ['baz'], None, True),
    ({'foo': 'bar'}, ['foo', 'baz'], None, True),
    ({'foo': 'bar'}, [], {'foo': 'bar'}, False),
    ({'foo': ['bar', 'baz']}, ['foo', 0], 'bar', False),
    ({'foo': ['bar', 'baz']}, ['foo', 1], 'baz', False),
    ({'foo': ['bar', 'baz']}, ['foo', 2], None, True),
    (['foo', {'bar': 'baz'}], [1, 'bar'], 'baz', False),

]

@pytest.mark.parametrize('obj,path,expected,invalid', path_cases)
def test_get_path(obj, path, expected, invalid):
    assert get_path(obj, path) == expected
    if invalid:
        with pytest.raises(LookupError):
            get_path(obj, path, strict=True)
    else:
        get_path(obj, path, strict=True)


key_step_cases = [
    ({'foo': 'bar'}, [], 'foo', [['foo']]),
    (['foo', 'bar'], [], 'foo', []),
    ('foo', [], 'foo', []),
    ({'foo': {'bar': 'baz'}}, ['foo'], 'bar', [['foo', 'bar']]),
    ({'foo': {'bar': 'baz'}}, ['foo'], 'baz', []),
    ({'foo': [{'bar': 'baz'}]}, ['foo', 0], 'bar', [['foo', 0, 'bar']]),
]

@pytest.mark.parametrize('obj,path,key,expected', key_step_cases)
def test_key_step(obj, path, key, expected):
    step = Key(key)
    result = list(step.find_in_tree(obj, path))
    assert result == expected


index_step_cases = [
    (['foo', 'bar'], [], 0, [[0]]),
    (['foo', 'bar'], [], 1, [[1]]),
    (['foo', 'bar'], [], 2, []),
    (['foo', 'bar'], [], -1, [[1]]),
    (['foo', 'bar'], [], -5, []),
    ('foo', [], 0, []),
    ({'foo': 'bar'}, [], 0, []),
    ({'foo': ['bar', 'baz']}, ['foo'], 0, [['foo', 0]]),
]

@pytest.mark.parametrize('obj,path,index,expected', index_step_cases)
def test_index_step(obj, path, index, expected):
    step = Index(index)
    result = list(step.find_in_tree(obj, path))
    assert result == expected
