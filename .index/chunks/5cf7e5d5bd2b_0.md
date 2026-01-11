# Chunk: 5cf7e5d5bd2b_0

- source: `.venv-lab/Lib/site-packages/IPython/utils/ipstruct.py`
- lines: 1-105
- chunk: 1/5

```
# encoding: utf-8
"""A dict subclass that supports attribute style access.

Authors:

* Fernando Perez (original)
* Brian Granger (refactoring to a dict subclass)
"""

#-----------------------------------------------------------------------------
#  Copyright (C) 2008-2011  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

__all__ = ['Struct']

#-----------------------------------------------------------------------------
# Code
#-----------------------------------------------------------------------------


class Struct(dict):
    """A dict subclass with attribute style access.

    This dict subclass has a a few extra features:

    * Attribute style access.
    * Protection of class members (like keys, items) when using attribute
      style access.
    * The ability to restrict assignment to only existing keys.
    * Intelligent merging.
    * Overloaded operators.
    """
    _allownew = True
    def __init__(self, *args, **kw):
        """Initialize with a dictionary, another Struct, or data.

        Parameters
        ----------
        *args : dict, Struct
            Initialize with one dict or Struct
        **kw : dict
            Initialize with key, value pairs.

        Examples
        --------
        >>> s = Struct(a=10,b=30)
        >>> s.a
        10
        >>> s.b
        30
        >>> s2 = Struct(s,c=30)
        >>> sorted(s2.keys())
        ['a', 'b', 'c']
        """
        object.__setattr__(self, '_allownew', True)
        dict.__init__(self, *args, **kw)

    def __setitem__(self, key, value):
        """Set an item with check for allownew.

        Examples
        --------
        >>> s = Struct()
        >>> s['a'] = 10
        >>> s.allow_new_attr(False)
        >>> s['a'] = 10
        >>> s['a']
        10
        >>> try:
        ...     s['b'] = 20
        ... except KeyError:
        ...     print('this is not allowed')
        ...
        this is not allowed
        """
        if not self._allownew and key not in self:
            raise KeyError(
                "can't create new attribute %s when allow_new_attr(False)" % key)
        dict.__setitem__(self, key, value)

    def __setattr__(self, key, value):
        """Set an attr with protection of class members.

        This calls :meth:`self.__setitem__` but convert :exc:`KeyError` to
        :exc:`AttributeError`.

        Examples
        --------
        >>> s = Struct()
        >>> s.a = 10
        >>> s.a
        10
        >>> try:
        ...     s.get = 10
        ... except AttributeError:
        ...     print("you can't set a class member")
        ...
```
