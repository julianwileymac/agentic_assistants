# Chunk: a179a3ecb1bf_2

- source: `.venv-lab/Lib/site-packages/bs4/element.py`
- lines: 190-268
- chunk: 3/45

```
ific encoding.
        """
        raise NotImplementedError()


class CharsetMetaAttributeValue(AttributeValueWithCharsetSubstitution):
    """A generic stand-in for the value of a ``<meta>`` tag's ``charset``
    attribute.

    When Beautiful Soup parses the markup ``<meta charset="utf8">``, the
    value of the ``charset`` attribute will become one of these objects.

    If the document is later encoded to an encoding other than UTF-8, its
    ``<meta>`` tag will mention the new encoding instead of ``utf8``.
    """

    def __new__(cls, original_value: str) -> Self:
        # We don't need to use the original value for anything, but
        # it might be useful for the user to know.
        obj = str.__new__(cls, original_value)
        obj.original_value = original_value
        return obj

    def substitute_encoding(self, eventual_encoding: _Encoding = "utf-8") -> str:
        """When an HTML document is being encoded to a given encoding, the
        value of a ``<meta>`` tag's ``charset`` becomes the name of
        the encoding.
        """
        if eventual_encoding in PYTHON_SPECIFIC_ENCODINGS:
            return ""
        return eventual_encoding


class AttributeValueList(List[str]):
    """Class for the list used to hold the values of attributes which
    have multiple values (such as HTML's 'class'). It's just a regular
    list, but you can subclass it and pass it in to the TreeBuilder
    constructor as attribute_value_list_class, to have your subclass
    instantiated instead.
    """


class AttributeDict(Dict[Any,Any]):
    """Superclass for the dictionary used to hold a tag's
    attributes. You can use this, but it's just a regular dict with no
    special logic.
    """


class XMLAttributeDict(AttributeDict):
    """A dictionary for holding a Tag's attributes, which processes
    incoming values for consistency with the HTML spec.
    """

    def __setitem__(self, key: str, value: Any) -> None:
        """Set an attribute value, possibly modifying it to comply with
        the XML spec.

        This just means converting common non-string values to
        strings: XML attributes may have "any literal string as a
        value."
        """
        if value is None:
            value = ""
        if isinstance(value, bool):
            # XML does not define any rules for boolean attributes.
            # Preserve the old Beautiful Soup behavior (a bool that
            # gets converted to a string on output) rather than
            # guessing what the value should be.
            pass
        elif isinstance(value, (int, float)):
            # It's dangerous to convert _every_ attribute value into a
            # plain string, since an attribute value may be a more
            # sophisticated string-like object
            # (e.g. CharsetMetaAttributeValue). But we can definitely
            # convert numeric values and booleans, which are the most common.
            value = str(value)
```
