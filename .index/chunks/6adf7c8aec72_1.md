# Chunk: 6adf7c8aec72_1

- source: `.venv-lab/Lib/site-packages/bs4/diagnose.py`
- lines: 92-203
- chunk: 2/3

```
etermine whether
    an lxml-specific problem is in Beautiful Soup's lxml tree builders
    or in lxml itself.

    :param data: Some markup.
    :param html: If True, markup will be parsed with lxml's HTML parser.
       if False, lxml's XML parser will be used.
    """
    from lxml import etree

    recover = kwargs.pop("recover", True)
    if isinstance(data, str):
        data = data.encode("utf8")
    if not isinstance(data, IO):
        reader = BytesIO(data)
    for event, element in etree.iterparse(reader, html=html, recover=recover, **kwargs):
        print(("%s, %4s, %s" % (event, element.tag, element.text)))


class AnnouncingParser(HTMLParser):
    """Subclass of HTMLParser that announces parse events, without doing
    anything else.

    You can use this to get a picture of how html.parser sees a given
    document. The easiest way to do this is to call `htmlparser_trace`.
    """

    def _p(self, s: str) -> None:
        print(s)

    def handle_starttag(
        self,
        name: str,
        attrs: List[Tuple[str, Optional[str]]],
        handle_empty_element: bool = True,
    ) -> None:
        self._p(f"{name} {attrs} START")

    def handle_endtag(self, name: str, check_already_closed: bool = True) -> None:
        self._p("%s END" % name)

    def handle_data(self, data: str) -> None:
        self._p("%s DATA" % data)

    def handle_charref(self, name: str) -> None:
        self._p("%s CHARREF" % name)

    def handle_entityref(self, name: str) -> None:
        self._p("%s ENTITYREF" % name)

    def handle_comment(self, data: str) -> None:
        self._p("%s COMMENT" % data)

    def handle_decl(self, data: str) -> None:
        self._p("%s DECL" % data)

    def unknown_decl(self, data: str) -> None:
        self._p("%s UNKNOWN-DECL" % data)

    def handle_pi(self, data: str) -> None:
        self._p("%s PI" % data)


def htmlparser_trace(data: str) -> None:
    """Print out the HTMLParser events that occur during parsing.

    This lets you see how HTMLParser parses a document when no
    Beautiful Soup code is running.

    :param data: Some markup.
    """
    parser = AnnouncingParser()
    parser.feed(data)


_vowels: str = "aeiou"
_consonants: str = "bcdfghjklmnpqrstvwxyz"


def rword(length: int = 5) -> str:
    """Generate a random word-like string.

    :meta private:
    """
    s = ""
    for i in range(length):
        if i % 2 == 0:
            t = _consonants
        else:
            t = _vowels
        s += random.choice(t)
    return s


def rsentence(length: int = 4) -> str:
    """Generate a random sentence-like string.

    :meta private:
    """
    return " ".join(rword(random.randint(4, 9)) for i in range(length))


def rdoc(num_elements: int = 1000) -> str:
    """Randomly generate an invalid HTML document.

    :meta private:
    """
    tag_names = ["p", "div", "span", "i", "b", "script", "table"]
    elements = []
    for i in range(num_elements):
        choice = random.randint(0, 3)
```
