# Chunk: cc40ffdf0eb4_0

- source: `.venv-lab/Lib/site-packages/mistune/block_parser.py`
- lines: 1-107
- chunk: 1/7

```
import re
from typing import Optional, List, Tuple, Match, Pattern
import string
from .util import (
    unikey,
    escape_url,
    expand_tab,
    expand_leading_tab,
)
from .core import Parser, BlockState
from .helpers import (
    LINK_LABEL,
    HTML_TAGNAME,
    HTML_ATTRIBUTES,
    BLOCK_TAGS,
    PRE_TAGS,
    unescape_char,
    parse_link_href,
    parse_link_title,
)
from .list_parser import parse_list, LIST_PATTERN

_INDENT_CODE_TRIM = re.compile(r"^ {1,4}", flags=re.M)
_ATX_HEADING_TRIM = re.compile(r"(\s+|^)#+\s*$")
_BLOCK_QUOTE_TRIM = re.compile(r"^ ?", flags=re.M)
_BLOCK_QUOTE_LEADING = re.compile(r"^ *>", flags=re.M)

_LINE_BLANK_END = re.compile(r"\n[ \t]*\n$")
_BLANK_TO_LINE = re.compile(r"[ \t]*\n")

_BLOCK_TAGS_PATTERN = "(" + "|".join(BLOCK_TAGS) + "|" + "|".join(PRE_TAGS) + ")"
_OPEN_TAG_END = re.compile(HTML_ATTRIBUTES + r"[ \t]*>[ \t]*(?:\n|$)")
_CLOSE_TAG_END = re.compile(r"[ \t]*>[ \t]*(?:\n|$)")
_STRICT_BLOCK_QUOTE = re.compile(r"( {0,3}>[^\n]*(?:\n|$))+")


class BlockParser(Parser[BlockState]):
    state_cls = BlockState

    BLANK_LINE = re.compile(r"(^[ \t\v\f]*\n)+", re.M)

    RAW_HTML = (
        r"^ {0,3}("
        r"</?" + HTML_TAGNAME + r"|"
        r"<!--|"  # comment
        r"<\?|"  # script
        r"<![A-Z]|"
        r"<!\[CDATA\[)"
    )

    BLOCK_HTML = (
        r"^ {0,3}(?:"
        r"(?:</?" + _BLOCK_TAGS_PATTERN + r"(?:[ \t]+|\n|$))"
        r"|<!--"  # comment
        r"|<\?"  # script
        r"|<![A-Z]"
        r"|<!\[CDATA\[)"
    )

    SPECIFICATION = {
        "blank_line": r"(^[ \t\v\f]*\n)+",
        "atx_heading": r"^ {0,3}(?P<atx_1>#{1,6})(?!#+)(?P<atx_2>[ \t]*|[ \t]+.*?)$",
        "setex_heading": r"^ {0,3}(?P<setext_1>=|-){1,}[ \t]*$",
        "fenced_code": (
            r"^(?P<fenced_1> {0,3})(?P<fenced_2>`{3,}|~{3,})"
            r"[ \t]*(?P<fenced_3>.*?)$"
        ),
        "indent_code": (
            r"^(?: {4}| *\t)[^\n]+(?:\n+|$)"
            r"((?:(?: {4}| *\t)[^\n]+(?:\n+|$))|\s)*"
        ),
        "thematic_break": r"^ {0,3}((?:-[ \t]*){3,}|(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})$",
        "ref_link": r"^ {0,3}\[(?P<reflink_1>" + LINK_LABEL + r")\]:",
        "block_quote": r"^ {0,3}>(?P<quote_1>.*?)$",
        "list": LIST_PATTERN,
        "block_html": BLOCK_HTML,
        "raw_html": RAW_HTML,
    }

    DEFAULT_RULES = (
        "fenced_code",
        "indent_code",
        "atx_heading",
        "setex_heading",
        "thematic_break",
        "block_quote",
        "list",
        "ref_link",
        "raw_html",
        "blank_line",
    )

    def __init__(
        self,
        block_quote_rules: Optional[List[str]] = None,
        list_rules: Optional[List[str]] = None,
        max_nested_level: int = 6,
    ):
        super(BlockParser, self).__init__()

        if block_quote_rules is None:
            block_quote_rules = list(self.DEFAULT_RULES)

        if list_rules is None:
            list_rules = list(self.DEFAULT_RULES)
```
