# Chunk: a179a3ecb1bf_5

- source: `.venv-lab/Lib/site-packages/bs4/element.py`
- lines: 398-479
- chunk: 6/45

```
ediately after
            this one.

        :param previous_sibling: The most recently encountered element
            on the same level of the parse tree as this one.

        :param previous_sibling: The next element to be encountered
            on the same level of the parse tree as this one.
        """
        self.parent = parent

        self.previous_element = previous_element
        if self.previous_element is not None:
            self.previous_element.next_element = self

        self.next_element = next_element
        if self.next_element is not None:
            self.next_element.previous_element = self

        self.next_sibling = next_sibling
        if self.next_sibling is not None:
            self.next_sibling.previous_sibling = self

        if (
            previous_sibling is None
            and self.parent is not None
            and self.parent.contents
        ):
            previous_sibling = self.parent.contents[-1]

        self.previous_sibling = previous_sibling
        if self.previous_sibling is not None:
            self.previous_sibling.next_sibling = self

    def format_string(self, s: str, formatter: Optional[_FormatterOrName]) -> str:
        """Format the given string using the given formatter.

        :param s: A string.
        :param formatter: A Formatter object, or a string naming one of the standard formatters.
        """
        if formatter is None:
            return s
        if not isinstance(formatter, Formatter):
            formatter = self.formatter_for_name(formatter)
        output = formatter.substitute(s)
        return output

    def formatter_for_name(
        self, formatter_name: Union[_FormatterOrName, _EntitySubstitutionFunction]
    ) -> Formatter:
        """Look up or create a Formatter for the given identifier,
        if necessary.

        :param formatter: Can be a `Formatter` object (used as-is), a
            function (used as the entity substitution hook for an
            `bs4.formatter.XMLFormatter` or
            `bs4.formatter.HTMLFormatter`), or a string (used to look
            up an `bs4.formatter.XMLFormatter` or
            `bs4.formatter.HTMLFormatter` in the appropriate registry.

        """
        if isinstance(formatter_name, Formatter):
            return formatter_name
        c: type[Formatter]
        registry: Mapping[Optional[str], Formatter]
        if self._is_xml:
            c = XMLFormatter
            registry = XMLFormatter.REGISTRY
        else:
            c = HTMLFormatter
            registry = HTMLFormatter.REGISTRY
        if callable(formatter_name):
            return c(entity_substitution=formatter_name)
        return registry[formatter_name]

    @property
    def _is_xml(self) -> bool:
        """Is this element part of an XML tree or an HTML tree?

        This is used in formatter_for_name, when deciding whether an
        XMLFormatter or HTMLFormatter is more appropriate. It can be
```
