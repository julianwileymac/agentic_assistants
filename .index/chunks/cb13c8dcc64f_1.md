# Chunk: cb13c8dcc64f_1

- source: `.venv-lab/Lib/site-packages/debugpy/common/singleton.py`
- lines: 58-130
- chunk: 2/3

```
 stub will get auto-invoked on return,
                        # and on all future singleton accesses.
                        cls._instance.__init__()
                        cls.__init__ = lambda *args, **kwargs: None

        return cls._instance

    def __init__(self, *args, **kwargs):
        """Initializes the singleton instance. Guaranteed to only be invoked once for
        any given type derived from Singleton.

        If shared=False, the caller is requesting a singleton instance for their own
        exclusive use. This is only allowed if the singleton has not been created yet;
        if so, it is created and marked as being in exclusive use. While it is marked
        as such, all attempts to obtain an existing instance of it immediately raise
        an exception. The singleton can eventually be promoted to shared use by calling
        share() on it.
        """

        shared = kwargs.pop("shared", True)
        with self:
            if shared:
                assert (
                    type(self)._is_shared is not False
                ), "Cannot access a non-shared Singleton."
                type(self)._is_shared = True
            else:
                assert type(self)._is_shared is None, "Singleton is already created."

    def __enter__(self):
        """Lock this singleton to prevent concurrent access."""
        type(self)._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Unlock this singleton to allow concurrent access."""
        type(self)._lock.release()

    def share(self):
        """Share this singleton, if it was originally created with shared=False."""
        type(self)._is_shared = True


class ThreadSafeSingleton(Singleton):
    """A singleton that incorporates a lock for thread-safe access to its members.

    The lock can be acquired using the context manager protocol, and thus idiomatic
    use is in conjunction with a with-statement. For example, given derived class T::

        with T() as t:
            t.x = t.frob(t.y)

    All access to the singleton from the outside should follow this pattern for both
    attributes and method calls. Singleton members can assume that self is locked by
    the caller while they're executing, but recursive locking of the same singleton
    on the same thread is also permitted.
    """

    threadsafe_attrs = frozenset()
    """Names of attributes that are guaranteed to be used in a thread-safe manner.

    This is typically used in conjunction with share() to simplify synchronization.
    """

    readonly_attrs = frozenset()
    """Names of attributes that are readonly. These can be read without locking, but
    cannot be written at all.

    Every derived class gets its own separate set. Thus, for any given singleton type
    T, an attribute can be made readonly after setting it, with T.readonly_attrs.add().
    """

```
