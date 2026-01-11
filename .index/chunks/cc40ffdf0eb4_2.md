# Chunk: cc40ffdf0eb4_2

- source: `.venv-lab/Lib/site-packages/mistune/block_parser.py`
- lines: 173-263
- chunk: 3/7

```
        if spaces and code:
            _trim_pattern = re.compile("^ {0," + str(len(spaces)) + "}", re.M)
            code = _trim_pattern.sub("", code)

        token = {"type": "block_code", "raw": code, "style": "fenced", "marker": marker}
        if info:
            info = unescape_char(info)
            token["attrs"] = {"info": info.strip()}

        state.append_token(token)
        return end_pos

    def parse_atx_heading(self, m: Match[str], state: BlockState) -> int:
        """Parse token for ATX heading. An ATX heading is started with 1 to 6
        symbol of ``#``."""
        level = len(m.group("atx_1"))
        text = m.group("atx_2").strip(string.whitespace)
        # remove last #
        if text:
            text = _ATX_HEADING_TRIM.sub("", text)

        token = {"type": "heading", "text": text, "attrs": {"level": level}, "style": "atx"}
        state.append_token(token)
        return m.end() + 1

    def parse_setex_heading(self, m: Match[str], state: BlockState) -> Optional[int]:
        """Parse token for setex style heading. A setex heading syntax looks like:

        .. code-block:: markdown

            H1 title
            ========
        """
        last_token = state.last_token()
        if last_token and last_token["type"] == "paragraph":
            level = 1 if m.group("setext_1") == "=" else 2
            last_token["type"] = "heading"
            last_token["style"] = "setext"
            last_token["attrs"] = {"level": level}
            return m.end() + 1

        sc = self.compile_sc(["thematic_break", "list"])
        m2 = sc.match(state.src, state.cursor)
        if m2:
            return self.parse_method(m2, state)
        return None

    def parse_ref_link(self, m: Match[str], state: BlockState) -> Optional[int]:
        """Parse link references and save the link information into ``state.env``.

        Here is an example of a link reference:

        .. code-block:: markdown

            a [link][example]

            [example]: https://example.com "Optional title"

        This method will save the link reference into ``state.env`` as::

            state.env['ref_links']['example'] = {
                'url': 'https://example.com',
                'title': "Optional title",
            }
        """
        end_pos = state.append_paragraph()
        if end_pos:
            return end_pos

        label = m.group("reflink_1")
        key = unikey(label)
        if not key:
            return None

        href, href_pos = parse_link_href(state.src, m.end(), block=True)
        if href is None:
            return None

        assert href_pos is not None

        _blank = self.BLANK_LINE.search(state.src, href_pos)
        if _blank:
            max_pos = _blank.start()
        else:
            max_pos = state.cursor_max

        title, title_pos = parse_link_title(state.src, href_pos, max_pos)
        if title_pos:
            m2 = _BLANK_TO_LINE.match(state.src, title_pos)
            if m2:
```
