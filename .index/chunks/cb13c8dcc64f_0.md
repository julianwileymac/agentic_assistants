# Chunk: cb13c8dcc64f_0

- source: `.venv-lab/Lib/site-packages/debugpy/common/singleton.py`
- lines: 1-66
- chunk: 1/3

```
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root
# for license information.

import functools
import threading


class Singleton(object):
    """A base class for a class of a singleton object.

    For any derived class T, the first invocation of T() will create the instance,
    and any future invocations of T() will return that instance.

    Concurrent invocations of T() from different threads are safe.
    """

    # A dual-lock scheme is necessary to be thread safe while avoiding deadlocks.
    # _lock_lock is shared by all singleton types, and is used to construct their
    # respective _lock instances when invoked for a new type. Then _lock is used
    # to synchronize all further access for that type, including __init__. This way,
    # __init__ for any given singleton can access another singleton, and not get
    # deadlocked if that other singleton is trying to access it.
    _lock_lock = threading.RLock()
    _lock = None

    # Specific subclasses will get their own _instance set in __new__.
    _instance = None

    _is_shared = None  # True if shared, False if exclusive

    def __new__(cls, *args, **kwargs):
        # Allow arbitrary args and kwargs if shared=False, because that is guaranteed
        # to construct a new singleton if it succeeds. Otherwise, this call might end
        # up returning an existing instance, which might have been constructed with
        # different arguments, so allowing them is misleading.
        assert not kwargs.get("shared", False) or (len(args) + len(kwargs)) == 0, (
            "Cannot use constructor arguments when accessing a Singleton without "
            "specifying shared=False."
        )

        # Avoid locking as much as possible with repeated double-checks - the most
        # common path is when everything is already allocated.
        if not cls._instance:
            # If there's no per-type lock, allocate it.
            if cls._lock is None:
                with cls._lock_lock:
                    if cls._lock is None:
                        cls._lock = threading.RLock()

            # Now that we have a per-type lock, we can synchronize construction.
            if not cls._instance:
                with cls._lock:
                    if not cls._instance:
                        cls._instance = object.__new__(cls)
                        # To prevent having __init__ invoked multiple times, call
                        # it here directly, and then replace it with a stub that
                        # does nothing - that stub will get auto-invoked on return,
                        # and on all future singleton accesses.
                        cls._instance.__init__()
                        cls.__init__ = lambda *args, **kwargs: None

        return cls._instance

    def __init__(self, *args, **kwargs):
```
