# Chunk: 0dbddc1f8b3f_1

- source: `.venv-lab/Lib/site-packages/bleach/_vendor/html5lib/_utils.py`
- lines: 83-160
- chunk: 2/2

```
__get__
        # on a function, __get__ is used to bind a function to an instance as a bound method
        return self.dispatcher[key].__get__(self.instance)

    def get(self, key, default):
        if key in self.dispatcher:
            return self[key]
        else:
            return default

    def __iter__(self):
        return iter(self.dispatcher)

    def __len__(self):
        return len(self.dispatcher)

    def __contains__(self, key):
        return key in self.dispatcher


# Some utility functions to deal with weirdness around UCS2 vs UCS4
# python builds

def isSurrogatePair(data):
    return (len(data) == 2 and
            ord(data[0]) >= 0xD800 and ord(data[0]) <= 0xDBFF and
            ord(data[1]) >= 0xDC00 and ord(data[1]) <= 0xDFFF)


def surrogatePairToCodepoint(data):
    char_val = (0x10000 + (ord(data[0]) - 0xD800) * 0x400 +
                (ord(data[1]) - 0xDC00))
    return char_val

# Module Factory Factory (no, this isn't Java, I know)
# Here to stop this being duplicated all over the place.


def moduleFactoryFactory(factory):
    moduleCache = {}

    def moduleFactory(baseModule, *args, **kwargs):
        if isinstance(ModuleType.__name__, type("")):
            name = "_%s_factory" % baseModule.__name__
        else:
            name = b"_%s_factory" % baseModule.__name__

        kwargs_tuple = tuple(kwargs.items())

        try:
            return moduleCache[name][args][kwargs_tuple]
        except KeyError:
            mod = ModuleType(name)
            objs = factory(baseModule, *args, **kwargs)
            mod.__dict__.update(objs)
            if "name" not in moduleCache:
                moduleCache[name] = {}
            if "args" not in moduleCache[name]:
                moduleCache[name][args] = {}
            if "kwargs" not in moduleCache[name][args]:
                moduleCache[name][args][kwargs_tuple] = {}
            moduleCache[name][args][kwargs_tuple] = mod
            return mod

    return moduleFactory


def memoize(func):
    cache = {}

    def wrapped(*args, **kwargs):
        key = (tuple(args), tuple(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapped
```
