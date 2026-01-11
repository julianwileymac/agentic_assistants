# Chunk: a179a3ecb1bf_6

- source: `.venv-lab/Lib/site-packages/bs4/element.py`
- lines: 470-548
- chunk: 7/45

```
tter_name)
        return registry[formatter_name]

    @property
    def _is_xml(self) -> bool:
        """Is this element part of an XML tree or an HTML tree?

        This is used in formatter_for_name, when deciding whether an
        XMLFormatter or HTMLFormatter is more appropriate. It can be
        inefficient, but it should be called very rarely.
        """
        if self.known_xml is not None:
            # Most of the time we will have determined this when the
            # document is parsed.
            return self.known_xml

        # Otherwise, it's likely that this element was created by
        # direct invocation of the constructor from within the user's
        # Python code.
        if self.parent is None:
            # This is the top-level object. It should have .known_xml set
            # from tree creation. If not, take a guess--BS is usually
            # used on HTML markup.
            return getattr(self, "is_xml", False)
        return self.parent._is_xml

    nextSibling = _deprecated_alias("nextSibling", "next_sibling", "4.0.0")
    previousSibling = _deprecated_alias("previousSibling", "previous_sibling", "4.0.0")

    def __deepcopy__(self, memo: Dict[Any, Any], recursive: bool = False) -> Self:
        raise NotImplementedError()

    def __copy__(self) -> Self:
        """A copy of a PageElement can only be a deep copy, because
        only one PageElement can occupy a given place in a parse tree.
        """
        return self.__deepcopy__({})

    default: Iterable[type[NavigableString]] = tuple()  #: :meta private:

    def _all_strings(
        self, strip: bool = False, types: Iterable[type[NavigableString]] = default
    ) -> Iterator[str]:
        """Yield all strings of certain classes, possibly stripping them.

        This is implemented differently in `Tag` and `NavigableString`.
        """
        raise NotImplementedError()

    @property
    def stripped_strings(self) -> Iterator[str]:
        """Yield all interesting strings in this PageElement, stripping them
        first.

        See `Tag` for information on which strings are considered
        interesting in a given context.
        """
        for string in self._all_strings(True):
            yield string

    def get_text(
        self,
        separator: str = "",
        strip: bool = False,
        types: Iterable[Type[NavigableString]] = default,
    ) -> str:
        """Get all child strings of this PageElement, concatenated using the
        given separator.

        :param separator: Strings will be concatenated using this separator.

        :param strip: If True, strings will be stripped before being
            concatenated.

        :param types: A tuple of NavigableString subclasses. Any
            strings of a subclass not found in this list will be
            ignored. Although there are exceptions, the default
            behavior in most cases is to consider only NavigableString
```
