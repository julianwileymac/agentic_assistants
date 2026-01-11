# Chunk: 3dcd7e4aa8d6_4

- source: `.venv-lab/Lib/site-packages/setuptools/_vendor/jaraco/collections/__init__.py`
- lines: 369-503
- chunk: 5/10

```
       """
        try:
            return next(e_key for e_key in self.keys() if e_key == key)
        except StopIteration as err:
            raise KeyError(key) from err


class FoldedCaseKeyedDict(KeyTransformingDict):
    """
    A case-insensitive dictionary (keys are compared as insensitive
    if they are strings).

    >>> d = FoldedCaseKeyedDict()
    >>> d['heLlo'] = 'world'
    >>> list(d.keys()) == ['heLlo']
    True
    >>> list(d.values()) == ['world']
    True
    >>> d['hello'] == 'world'
    True
    >>> 'hello' in d
    True
    >>> 'HELLO' in d
    True
    >>> print(repr(FoldedCaseKeyedDict({'heLlo': 'world'})))
    {'heLlo': 'world'}
    >>> d = FoldedCaseKeyedDict({'heLlo': 'world'})
    >>> print(d['hello'])
    world
    >>> print(d['Hello'])
    world
    >>> list(d.keys())
    ['heLlo']
    >>> d = FoldedCaseKeyedDict({'heLlo': 'world', 'Hello': 'world'})
    >>> list(d.values())
    ['world']
    >>> key, = d.keys()
    >>> key in ['heLlo', 'Hello']
    True
    >>> del d['HELLO']
    >>> d
    {}

    get should work

    >>> d['Sumthin'] = 'else'
    >>> d.get('SUMTHIN')
    'else'
    >>> d.get('OTHER', 'thing')
    'thing'
    >>> del d['sumthin']

    setdefault should also work

    >>> d['This'] = 'that'
    >>> print(d.setdefault('this', 'other'))
    that
    >>> len(d)
    1
    >>> print(d['this'])
    that
    >>> print(d.setdefault('That', 'other'))
    other
    >>> print(d['THAT'])
    other

    Make it pop!

    >>> print(d.pop('THAT'))
    other

    To retrieve the key in its originally-supplied form, use matching_key_for

    >>> print(d.matching_key_for('this'))
    This

    >>> d.matching_key_for('missing')
    Traceback (most recent call last):
    ...
    KeyError: 'missing'
    """

    @staticmethod
    def transform_key(key):
        return jaraco.text.FoldedCase(key)


class DictAdapter:
    """
    Provide a getitem interface for attributes of an object.

    Let's say you want to get at the string.lowercase property in a formatted
    string. It's easy with DictAdapter.

    >>> import string
    >>> print("lowercase is %(ascii_lowercase)s" % DictAdapter(string))
    lowercase is abcdefghijklmnopqrstuvwxyz
    """

    def __init__(self, wrapped_ob):
        self.object = wrapped_ob

    def __getitem__(self, name):
        return getattr(self.object, name)


class ItemsAsAttributes:
    """
    Mix-in class to enable a mapping object to provide items as
    attributes.

    >>> C = type('C', (dict, ItemsAsAttributes), dict())
    >>> i = C()
    >>> i['foo'] = 'bar'
    >>> i.foo
    'bar'

    Natural attribute access takes precedence

    >>> i.foo = 'henry'
    >>> i.foo
    'henry'

    But as you might expect, the mapping functionality is preserved.

    >>> i['foo']
    'bar'

    A normal attribute error should be raised if an attribute is
    requested that doesn't exist.

    >>> i.missing
    Traceback (most recent call last):
    ...
```
