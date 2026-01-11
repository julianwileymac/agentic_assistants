# Chunk: cc40ffdf0eb4_1

- source: `.venv-lab/Lib/site-packages/mistune/block_parser.py`
- lines: 96-180
- chunk: 2/7

```
rules: Optional[List[str]] = None,
        max_nested_level: int = 6,
    ):
        super(BlockParser, self).__init__()

        if block_quote_rules is None:
            block_quote_rules = list(self.DEFAULT_RULES)

        if list_rules is None:
            list_rules = list(self.DEFAULT_RULES)

        self.block_quote_rules = block_quote_rules
        self.list_rules = list_rules
        self.max_nested_level = max_nested_level
        # register default parse methods
        self._methods = {name: getattr(self, "parse_" + name) for name in self.SPECIFICATION}

    def parse_blank_line(self, m: Match[str], state: BlockState) -> int:
        """Parse token for blank lines."""
        state.append_token({"type": "blank_line"})
        return m.end()

    def parse_thematic_break(self, m: Match[str], state: BlockState) -> int:
        """Parse token for thematic break, e.g. ``<hr>`` tag in HTML."""
        state.append_token({"type": "thematic_break"})
        # $ does not count '\n'
        return m.end() + 1

    def parse_indent_code(self, m: Match[str], state: BlockState) -> int:
        """Parse token for code block which is indented by 4 spaces."""
        # it is a part of the paragraph
        end_pos = state.append_paragraph()
        if end_pos:
            return end_pos

        code = m.group(0)
        code = expand_leading_tab(code)
        code = _INDENT_CODE_TRIM.sub("", code)
        code = code.strip("\n")
        state.append_token({"type": "block_code", "raw": code, "style": "indent"})
        return m.end()

    def parse_fenced_code(self, m: Match[str], state: BlockState) -> Optional[int]:
        """Parse token for fenced code block. A fenced code block is started with
        3 or more backtick(`) or tilde(~).

        An example of a fenced code block:

        .. code-block:: markdown

            ```python
            def markdown(text):
                return mistune.html(text)
            ```
        """
        spaces = m.group("fenced_1")
        marker = m.group("fenced_2")
        info = m.group("fenced_3")

        c = marker[0]
        if info and c == "`":
            # CommonMark Example 145
            # Info strings for backtick code blocks cannot contain backticks
            if info.find(c) != -1:
                return None

        _end = re.compile(r"^ {0,3}" + c + "{" + str(len(marker)) + r",}[ \t]*(?:\n|$)", re.M)
        cursor_start = m.end() + 1

        m2 = _end.search(state.src, cursor_start)
        if m2:
            code = state.src[cursor_start : m2.start()]
            end_pos = m2.end()
        else:
            code = state.src[cursor_start:]
            end_pos = state.cursor_max

        if spaces and code:
            _trim_pattern = re.compile("^ {0," + str(len(spaces)) + "}", re.M)
            code = _trim_pattern.sub("", code)

        token = {"type": "block_code", "raw": code, "style": "fenced", "marker": marker}
        if info:
            info = unescape_char(info)
```
