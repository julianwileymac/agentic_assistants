# Chunk: 1bfb27fbc0ca_1

- source: `.venv-lab/Lib/site-packages/pip/_vendor/rich/highlighter.py`
- lines: 91-163
- chunk: 2/4

```
9A-Fa-f]{4})",
            r"(?P<eui48>(?:[0-9A-Fa-f]{1,2}-){5}[0-9A-Fa-f]{1,2}|(?:[0-9A-Fa-f]{1,2}:){5}[0-9A-Fa-f]{1,2}|(?:[0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4})",
            r"(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})",
            r"(?P<call>[\w.]*?)\(",
            r"\b(?P<bool_true>True)\b|\b(?P<bool_false>False)\b|\b(?P<none>None)\b",
            r"(?P<ellipsis>\.\.\.)",
            r"(?P<number_complex>(?<!\w)(?:\-?[0-9]+\.?[0-9]*(?:e[-+]?\d+?)?)(?:[-+](?:[0-9]+\.?[0-9]*(?:e[-+]?\d+)?))?j)",
            r"(?P<number>(?<!\w)\-?[0-9]+\.?[0-9]*(e[-+]?\d+?)?\b|0x[0-9a-fA-F]*)",
            r"(?P<path>\B(/[-\w._+]+)*\/)(?P<filename>[-\w._+]*)?",
            r"(?<![\\\w])(?P<str>b?'''.*?(?<!\\)'''|b?'.*?(?<!\\)'|b?\"\"\".*?(?<!\\)\"\"\"|b?\".*?(?<!\\)\")",
            r"(?P<url>(file|https|http|ws|wss)://[-0-9a-zA-Z$_+!`(),.?/;:&=%#~@]*)",
        ),
    ]


class JSONHighlighter(RegexHighlighter):
    """Highlights JSON"""

    # Captures the start and end of JSON strings, handling escaped quotes
    JSON_STR = r"(?<![\\\w])(?P<str>b?\".*?(?<!\\)\")"
    JSON_WHITESPACE = {" ", "\n", "\r", "\t"}

    base_style = "json."
    highlights = [
        _combine_regex(
            r"(?P<brace>[\{\[\(\)\]\}])",
            r"\b(?P<bool_true>true)\b|\b(?P<bool_false>false)\b|\b(?P<null>null)\b",
            r"(?P<number>(?<!\w)\-?[0-9]+\.?[0-9]*(e[\-\+]?\d+?)?\b|0x[0-9a-fA-F]*)",
            JSON_STR,
        ),
    ]

    def highlight(self, text: Text) -> None:
        super().highlight(text)

        # Additional work to handle highlighting JSON keys
        plain = text.plain
        append = text.spans.append
        whitespace = self.JSON_WHITESPACE
        for match in re.finditer(self.JSON_STR, plain):
            start, end = match.span()
            cursor = end
            while cursor < len(plain):
                char = plain[cursor]
                cursor += 1
                if char == ":":
                    append(Span(start, end, "json.key"))
                elif char in whitespace:
                    continue
                break


class ISO8601Highlighter(RegexHighlighter):
    """Highlights the ISO8601 date time strings.
    Regex reference: https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch04s07.html
    """

    base_style = "iso8601."
    highlights = [
        #
        # Dates
        #
        # Calendar month (e.g. 2008-08). The hyphen is required
        r"^(?P<year>[0-9]{4})-(?P<month>1[0-2]|0[1-9])$",
        # Calendar date w/o hyphens (e.g. 20080830)
        r"^(?P<date>(?P<year>[0-9]{4})(?P<month>1[0-2]|0[1-9])(?P<day>3[01]|0[1-9]|[12][0-9]))$",
        # Ordinal date (e.g. 2008-243). The hyphen is optional
        r"^(?P<date>(?P<year>[0-9]{4})-?(?P<day>36[0-6]|3[0-5][0-9]|[12][0-9]{2}|0[1-9][0-9]|00[1-9]))$",
        #
        # Weeks
        #
        # Week of the year (e.g., 2008-W35). The hyphen is optional
```
