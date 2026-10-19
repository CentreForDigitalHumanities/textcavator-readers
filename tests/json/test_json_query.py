import pytest
from textcavator_readers.json_utils import (
    is_primitive, get_path, Key, Index, Root, Path, Values, MultiValue,
    iterate_steps, Parent
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
    assert get_path(obj, path, strict=False) == expected
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


def test_root_step():
    step = Root()
    result = list(step.find_in_tree(
        {'foo': {'bar': 'baz'}},
        ['foo']
    ))
    assert result == [[]]

path_step_cases = [
    ({'foo': 'bar'}, [], ['foo'], [['foo']]),
    (['foo', 'bar'], [], ['foo'], []),
    ('foo', [], 'foo', []),
    ({'foo': {'bar': 'baz'}}, ['foo'], ['bar'], [['foo', 'bar']]),
    ({'foo': {'bar': 'baz'}}, [], ['foo', 'bar'], [['foo', 'bar']]),
    ({'foo': {'bar': 'baz'}}, [], ['foo.bar'], [['foo', 'bar']]),
    ({'foo': {'bar': 'baz'}}, ['foo'], ['baz'], []),
    ({'foo': [{'bar': 'baz'}]}, [], ['foo', 0, 'bar'], [['foo', 0, 'bar']]),
]


@pytest.mark.parametrize('obj,path,subpath,expected', path_step_cases)
def test_path_step(obj, path, subpath, expected):
    step = Path(*subpath)
    result = list(step.find_in_tree(obj, path))
    assert result == expected


def test_filter_step():
    doc = {'foo': {'bar': 'baz'}}
    func = lambda obj: isinstance(obj, dict)

    step = Key('foo', filter=func)
    assert list(step.iterate(doc, [])) == [['foo']]

    step = Key('bar', filter=func)
    assert list(step.iterate(doc, ['foo'])) == []


def test_values_step():
    step = Values()
    assert list(step.find_in_tree(['foo', 'bar'], [])) == [[0], [1]]
    assert list(step.find_in_tree({'foo': 1, 'bar': 2}, [])) == [['foo'], ['bar']]
    assert list(step.find_in_tree('foo', [])) == []
    assert list(step.find_in_tree({'foo': ['bar', 'baz']}, ['foo'])) == [['foo', 0], ['foo', 1]]


def test_multivalue():
    step = MultiValue()
    assert list(step.find_in_tree({'foo': 'bar'}, ['foo'])) == [['foo']]
    assert list(step.find_in_tree({'foo': ['bar', 'baz']}, ['foo'])) == [['foo', 0], ['foo', 1]]


def test_parent():
    step = Parent()
    assert list(step.find_in_tree({'foo': {'bar': 'baz'}}, ['foo', 'bar'])) == [['foo']]


def test_iterate_steps():
    steps = [Key('foo'), Values(), Key('bar')]
    doc = {
        'foo': [
            {'bar': 'baz1'},
            {'bar': 'baz2'},
            {'bar': 'baz3'},
        ]
    }
    assert list(iterate_steps(doc, [], steps)) == [
        (doc, ['foo', 0, 'bar']),
        (doc, ['foo', 1, 'bar']),
        (doc, ['foo', 2, 'bar']),
    ]
