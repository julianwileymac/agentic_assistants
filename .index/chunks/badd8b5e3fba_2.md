# Chunk: badd8b5e3fba_2

- source: `.venv-lab/Lib/site-packages/markupsafe/__init__.py`
- lines: 165-251
- chunk: 3/5

```


    def __repr__(self, /) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"

    def join(self, iterable: cabc.Iterable[str | _HasHTML], /) -> te.Self:
        return self.__class__(super().join(map(self.escape, iterable)))

    def split(  # type: ignore[override]
        self, /, sep: str | None = None, maxsplit: t.SupportsIndex = -1
    ) -> list[te.Self]:
        return [self.__class__(v) for v in super().split(sep, maxsplit)]

    def rsplit(  # type: ignore[override]
        self, /, sep: str | None = None, maxsplit: t.SupportsIndex = -1
    ) -> list[te.Self]:
        return [self.__class__(v) for v in super().rsplit(sep, maxsplit)]

    def splitlines(  # type: ignore[override]
        self, /, keepends: bool = False
    ) -> list[te.Self]:
        return [self.__class__(v) for v in super().splitlines(keepends)]

    def unescape(self, /) -> str:
        """Convert escaped markup back into a text string. This replaces
        HTML entities with the characters they represent.

        >>> Markup("Main &raquo; <em>About</em>").unescape()
        'Main » <em>About</em>'
        """
        from html import unescape

        return unescape(str(self))

    def striptags(self, /) -> str:
        """:meth:`unescape` the markup, remove tags, and normalize
        whitespace to single spaces.

        >>> Markup("Main &raquo;\t<em>About</em>").striptags()
        'Main » About'
        """
        value = str(self)

        # Look for comments then tags separately. Otherwise, a comment that
        # contains a tag would end early, leaving some of the comment behind.

        # keep finding comment start marks
        while (start := value.find("<!--")) != -1:
            # find a comment end mark beyond the start, otherwise stop
            if (end := value.find("-->", start)) == -1:
                break

            value = f"{value[:start]}{value[end + 3 :]}"

        # remove tags using the same method
        while (start := value.find("<")) != -1:
            if (end := value.find(">", start)) == -1:
                break

            value = f"{value[:start]}{value[end + 1 :]}"

        # collapse spaces
        value = " ".join(value.split())
        return self.__class__(value).unescape()

    @classmethod
    def escape(cls, s: t.Any, /) -> te.Self:
        """Escape a string. Calls :func:`escape` and ensures that for
        subclasses the correct type is returned.
        """
        rv = escape(s)

        if rv.__class__ is not cls:
            return cls(rv)

        return rv  # type: ignore[return-value]

    def __getitem__(self, key: t.SupportsIndex | slice, /) -> te.Self:
        return self.__class__(super().__getitem__(key))

    def capitalize(self, /) -> te.Self:
        return self.__class__(super().capitalize())

    def title(self, /) -> te.Self:
        return self.__class__(super().title())

```
