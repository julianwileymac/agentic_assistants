# Chunk: a179a3ecb1bf_1

- source: `.venv-lab/Lib/site-packages/bs4/element.py`
- lines: 108-200
- chunk: 2/45

```
em (so they should not show up in an XML or HTML document as that
#: document's encoding).
#:
#: If an XML document is encoded in one of these encodings, no encoding
#: will be mentioned in the XML declaration. If an HTML document is
#: encoded in one of these encodings, and the HTML document has a
#: <meta> tag that mentions an encoding, the encoding will be given as
#: the empty string.
#:
#: Source:
#: Python documentation, `Python Specific Encodings <https://docs.python.org/3/library/codecs.html#python-specific-encodings>`_
PYTHON_SPECIFIC_ENCODINGS: Set[_Encoding] = set(
    [
        "idna",
        "mbcs",
        "oem",
        "palmos",
        "punycode",
        "raw_unicode_escape",
        "undefined",
        "unicode_escape",
        "raw-unicode-escape",
        "unicode-escape",
        "string-escape",
        "string_escape",
    ]
)


class NamespacedAttribute(str):
    """A namespaced attribute (e.g. the 'xml:lang' in 'xml:lang="en"')
    which remembers the namespace prefix ('xml') and the name ('lang')
    that were used to create it.
    """

    prefix: Optional[str]
    name: Optional[str]
    namespace: Optional[str]

    def __new__(
        cls,
        prefix: Optional[str],
        name: Optional[str] = None,
        namespace: Optional[str] = None,
    ) -> Self:
        if not name:
            # This is the default namespace. Its name "has no value"
            # per https://www.w3.org/TR/xml-names/#defaulting
            name = None

        if not name:
            obj = str.__new__(cls, prefix)
        elif not prefix:
            # Not really namespaced.
            obj = str.__new__(cls, name)
        else:
            obj = str.__new__(cls, prefix + ":" + name)
        obj.prefix = prefix
        obj.name = name
        obj.namespace = namespace
        return obj


class AttributeValueWithCharsetSubstitution(str):
    """An abstract class standing in for a character encoding specified
    inside an HTML ``<meta>`` tag.

    Subclasses exist for each place such a character encoding might be
    found: either inside the ``charset`` attribute
    (`CharsetMetaAttributeValue`) or inside the ``content`` attribute
    (`ContentMetaAttributeValue`)

    This allows Beautiful Soup to replace that part of the HTML file
    with a different encoding when ouputting a tree as a string.
    """

    # The original, un-encoded value of the ``content`` attribute.
    #: :meta private:
    original_value: str

    def substitute_encoding(self, eventual_encoding: str) -> str:
        """Do whatever's necessary in this implementation-specific
        portion an HTML document to substitute in a specific encoding.
        """
        raise NotImplementedError()


class CharsetMetaAttributeValue(AttributeValueWithCharsetSubstitution):
    """A generic stand-in for the value of a ``<meta>`` tag's ``charset``
    attribute.

    When Beautiful Soup parses the markup ``<meta charset="utf8">``, the
```
