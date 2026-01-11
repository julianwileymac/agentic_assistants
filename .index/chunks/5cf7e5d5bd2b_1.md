# Chunk: 5cf7e5d5bd2b_1

- source: `.venv-lab/Lib/site-packages/IPython/utils/ipstruct.py`
- lines: 91-206
- chunk: 2/5

```
c:`KeyError` to
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
        you can't set a class member
        """
        # If key is an str it might be a class member or instance var
        if isinstance(key, str):
            # I can't simply call hasattr here because it calls getattr, which
            # calls self.__getattr__, which returns True for keys in
            # self._data.  But I only want keys in the class and in
            # self.__dict__
            if key in self.__dict__ or hasattr(Struct, key):
                raise AttributeError(
                    'attr %s is a protected member of class Struct.' % key
                )
        try:
            self.__setitem__(key, value)
        except KeyError as e:
            raise AttributeError(e) from e

    def __getattr__(self, key):
        """Get an attr by calling :meth:`dict.__getitem__`.

        Like :meth:`__setattr__`, this method converts :exc:`KeyError` to
        :exc:`AttributeError`.

        Examples
        --------
        >>> s = Struct(a=10)
        >>> s.a
        10
        >>> type(s.get)
        <...method'>
        >>> try:
        ...     s.b
        ... except AttributeError:
        ...     print("I don't have that key")
        ...
        I don't have that key
        """
        try:
            result = self[key]
        except KeyError as e:
            raise AttributeError(key) from e
        else:
            return result

    def __iadd__(self, other):
        """s += s2 is a shorthand for s.merge(s2).

        Examples
        --------
        >>> s = Struct(a=10,b=30)
        >>> s2 = Struct(a=20,c=40)
        >>> s += s2
        >>> sorted(s.keys())
        ['a', 'b', 'c']
        """
        self.merge(other)
        return self

    def __add__(self,other):
        """s + s2 -> New Struct made from s.merge(s2).

        Examples
        --------
        >>> s1 = Struct(a=10,b=30)
        >>> s2 = Struct(a=20,c=40)
        >>> s = s1 + s2
        >>> sorted(s.keys())
        ['a', 'b', 'c']
        """
        sout = self.copy()
        sout.merge(other)
        return sout

    def __sub__(self,other):
        """s1 - s2 -> remove keys in s2 from s1.

        Examples
        --------
        >>> s1 = Struct(a=10,b=30)
        >>> s2 = Struct(a=40)
        >>> s = s1 - s2
        >>> s
        {'b': 30}
        """
        sout = self.copy()
        sout -= other
        return sout

    def __isub__(self,other):
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
```
