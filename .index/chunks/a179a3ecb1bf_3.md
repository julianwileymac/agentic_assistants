# Chunk: a179a3ecb1bf_3

- source: `.venv-lab/Lib/site-packages/bs4/element.py`
- lines: 261-334
- chunk: 4/45

```
nto a
            # plain string, since an attribute value may be a more
            # sophisticated string-like object
            # (e.g. CharsetMetaAttributeValue). But we can definitely
            # convert numeric values and booleans, which are the most common.
            value = str(value)

        super().__setitem__(key, value)


class HTMLAttributeDict(AttributeDict):
    """A dictionary for holding a Tag's attributes, which processes
    incoming values for consistency with the HTML spec, which says
    'Attribute values are a mixture of text and character
    references...'

    Basically, this means converting common non-string values into
    strings, like XMLAttributeDict, though HTML also has some rules
    around boolean attributes that XML doesn't have.
    """

    def __setitem__(self, key: str, value: Any) -> None:
        """Set an attribute value, possibly modifying it to comply
        with the HTML spec,
        """
        if value in (False, None):
            # 'The values "true" and "false" are not allowed on
            # boolean attributes. To represent a false value, the
            # attribute has to be omitted altogether.'
            if key in self:
                del self[key]
            return
        if isinstance(value, bool):
            # 'If the [boolean] attribute is present, its value must
            # either be the empty string or a value that is an ASCII
            # case-insensitive match for the attribute's canonical
            # name, with no leading or trailing whitespace.'
            #
            # [fixme] It's not clear to me whether "canonical name"
            # means fully-qualified name, unqualified name, or
            # (probably not) name with namespace prefix. For now I'm
            # going with unqualified name.
            if isinstance(key, NamespacedAttribute):
                value = key.name
            else:
                value = key
        elif isinstance(value, (int, float)):
            # See note in XMLAttributeDict for the reasoning why we
            # only do this to numbers.
            value = str(value)
        super().__setitem__(key, value)


class ContentMetaAttributeValue(AttributeValueWithCharsetSubstitution):
    """A generic stand-in for the value of a ``<meta>`` tag's ``content``
    attribute.

    When Beautiful Soup parses the markup:
     ``<meta http-equiv="content-type" content="text/html; charset=utf8">``

    The value of the ``content`` attribute will become one of these objects.

    If the document is later encoded to an encoding other than UTF-8, its
    ``<meta>`` tag will mention the new encoding instead of ``utf8``.
    """

    #: Match the 'charset' argument inside the 'content' attribute
    #: of a <meta> tag.
    #: :meta private:
    CHARSET_RE: Pattern[str] = re.compile(r"((^|;)\s*charset=)([^;]*)", re.M)

    def __new__(cls, original_value: str) -> Self:
        cls.CHARSET_RE.search(original_value)
```
