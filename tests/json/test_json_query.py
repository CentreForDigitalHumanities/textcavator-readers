import pytest
from textcavator_readers.json.query import (
    is_primitive, get_path
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
