# Chunk: 5cf7e5d5bd2b_2

- source: `.venv-lab/Lib/site-packages/IPython/utils/ipstruct.py`
- lines: 193-291
- chunk: 3/5

```
b__(self,other):
        """Inplace remove keys from self that are in other.

        Examples
        --------
        >>> s1 = Struct(a=10,b=30)
        >>> s2 = Struct(a=40)
        >>> s1 -= s2
        >>> s1
        {'b': 30}
        """
        for k in other.keys():
            if k in self:
                del self[k]
        return self

    def __dict_invert(self, data):
        """Helper function for merge.

        Takes a dictionary whose values are lists and returns a dict with
        the elements of each list as keys and the original keys as values.
        """
        outdict = {}
        for k,lst in data.items():
            if isinstance(lst, str):
                lst = lst.split()
            for entry in lst:
                outdict[entry] = k
        return outdict

    def dict(self):
        return self

    def copy(self):
        """Return a copy as a Struct.

        Examples
        --------
        >>> s = Struct(a=10,b=30)
        >>> s2 = s.copy()
        >>> type(s2) is Struct
        True
        """
        return Struct(dict.copy(self))

    def hasattr(self, key):
        """hasattr function available as a method.

        Implemented like has_key.

        Examples
        --------
        >>> s = Struct(a=10)
        >>> s.hasattr('a')
        True
        >>> s.hasattr('b')
        False
        >>> s.hasattr('get')
        False
        """
        return key in self

    def allow_new_attr(self, allow = True):
        """Set whether new attributes can be created in this Struct.

        This can be used to catch typos by verifying that the attribute user
        tries to change already exists in this Struct.
        """
        object.__setattr__(self, '_allownew', allow)

    def merge(self, __loc_data__=None, __conflict_solve=None, **kw):
        """Merge two Structs with customizable conflict resolution.

        This is similar to :meth:`update`, but much more flexible. First, a
        dict is made from data+key=value pairs. When merging this dict with
        the Struct S, the optional dictionary 'conflict' is used to decide
        what to do.

        If conflict is not given, the default behavior is to preserve any keys
        with their current value (the opposite of the :meth:`update` method's
        behavior).

        Parameters
        ----------
        __loc_data__ : dict, Struct
            The data to merge into self
        __conflict_solve : dict
            The conflict policy dict.  The keys are binary functions used to
            resolve the conflict and the values are lists of strings naming
            the keys the conflict resolution function applies to.  Instead of
            a list of strings a space separated string can be used, like
            'a b c'.
        **kw : dict
            Additional key, value pairs to merge in

        Notes
        -----
        The `__conflict_solve` dict is a dictionary of binary functions which will be used to
```
