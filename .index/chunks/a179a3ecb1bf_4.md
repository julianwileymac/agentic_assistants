# Chunk: a179a3ecb1bf_4

- source: `.venv-lab/Lib/site-packages/bs4/element.py`
- lines: 324-406
- chunk: 5/45

```
.
    """

    #: Match the 'charset' argument inside the 'content' attribute
    #: of a <meta> tag.
    #: :meta private:
    CHARSET_RE: Pattern[str] = re.compile(r"((^|;)\s*charset=)([^;]*)", re.M)

    def __new__(cls, original_value: str) -> Self:
        cls.CHARSET_RE.search(original_value)
        obj = str.__new__(cls, original_value)
        obj.original_value = original_value
        return obj

    def substitute_encoding(self, eventual_encoding: _Encoding = "utf-8") -> str:
        """When an HTML document is being encoded to a given encoding, the
        value of the ``charset=`` in a ``<meta>`` tag's ``content`` becomes
        the name of the encoding.
        """
        if eventual_encoding in PYTHON_SPECIFIC_ENCODINGS:
            return self.CHARSET_RE.sub("", self.original_value)

        def rewrite(match: re.Match[str]) -> str:
            return match.group(1) + eventual_encoding

        return self.CHARSET_RE.sub(rewrite, self.original_value)


class PageElement(object):
    """An abstract class representing a single element in the parse tree.

    `NavigableString`, `Tag`, etc. are all subclasses of
    `PageElement`. For this reason you'll see a lot of methods that
    return `PageElement`, but you'll never see an actual `PageElement`
    object. For the most part you can think of `PageElement` as
    meaning "a `Tag` or a `NavigableString`."
    """

    #: In general, we can't tell just by looking at an element whether
    #: it's contained in an XML document or an HTML document. But for
    #: `Tag` objects (q.v.) we can store this information at parse time.
    #: :meta private:
    known_xml: Optional[bool] = None

    #: Whether or not this element has been decomposed from the tree
    #: it was created in.
    _decomposed: bool

    parent: Optional[Tag]
    next_element: _AtMostOneElement
    previous_element: _AtMostOneElement
    next_sibling: _AtMostOneElement
    previous_sibling: _AtMostOneElement

    #: Whether or not this element is hidden from generated output.
    #: Only the `BeautifulSoup` object itself is hidden.
    hidden: bool = False

    def setup(
        self,
        parent: Optional[Tag] = None,
        previous_element: _AtMostOneElement = None,
        next_element: _AtMostOneElement = None,
        previous_sibling: _AtMostOneElement = None,
        next_sibling: _AtMostOneElement = None,
    ) -> None:
        """Sets up the initial relations between this element and
        other elements.

        :param parent: The parent of this element.

        :param previous_element: The element parsed immediately before
            this one.

        :param next_element: The element parsed immediately after
            this one.

        :param previous_sibling: The most recently encountered element
            on the same level of the parse tree as this one.

        :param previous_sibling: The next element to be encountered
            on the same level of the parse tree as this one.
```
