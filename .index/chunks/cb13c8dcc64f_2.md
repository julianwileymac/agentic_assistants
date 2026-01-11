# Chunk: cb13c8dcc64f_2

- source: `.venv-lab/Lib/site-packages/debugpy/common/singleton.py`
- lines: 123-186
- chunk: 3/3

```
"Names of attributes that are readonly. These can be read without locking, but
    cannot be written at all.

    Every derived class gets its own separate set. Thus, for any given singleton type
    T, an attribute can be made readonly after setting it, with T.readonly_attrs.add().
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make sure each derived class gets a separate copy.
        type(self).readonly_attrs = set(type(self).readonly_attrs)

    # Prevent callers from reading or writing attributes without locking, except for
    # reading attributes listed in threadsafe_attrs, and methods specifically marked
    # with @threadsafe_method. Such methods should perform the necessary locking to
    # ensure thread safety for the callers.

    @staticmethod
    def assert_locked(self):
        lock = type(self)._lock
        assert lock.acquire(blocking=False), (
            "ThreadSafeSingleton accessed without locking. Either use with-statement, "
            "or if it is a method or property, mark it as @threadsafe_method or with "
            "@autolocked_method, as appropriate."
        )
        lock.release()

    def __getattribute__(self, name):
        value = object.__getattribute__(self, name)
        if name not in (type(self).threadsafe_attrs | type(self).readonly_attrs):
            if not getattr(value, "is_threadsafe_method", False):
                ThreadSafeSingleton.assert_locked(self)
        return value

    def __setattr__(self, name, value):
        assert name not in type(self).readonly_attrs, "This attribute is read-only."
        if name not in type(self).threadsafe_attrs:
            ThreadSafeSingleton.assert_locked(self)
        return object.__setattr__(self, name, value)


def threadsafe_method(func):
    """Marks a method of a ThreadSafeSingleton-derived class as inherently thread-safe.

    A method so marked must either not use any singleton state, or lock it appropriately.
    """

    func.is_threadsafe_method = True
    return func


def autolocked_method(func):
    """Automatically synchronizes all calls of a method of a ThreadSafeSingleton-derived
    class by locking the singleton for the duration of each call.
    """

    @functools.wraps(func)
    @threadsafe_method
    def lock_and_call(self, *args, **kwargs):
        with self:
            return func(self, *args, **kwargs)

    return lock_and_call
```
