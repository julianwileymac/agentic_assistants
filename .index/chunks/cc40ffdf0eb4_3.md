# Chunk: cc40ffdf0eb4_3

- source: `.venv-lab/Lib/site-packages/mistune/block_parser.py`
- lines: 253-339
- chunk: 4/7

```
src, href_pos)
        if _blank:
            max_pos = _blank.start()
        else:
            max_pos = state.cursor_max

        title, title_pos = parse_link_title(state.src, href_pos, max_pos)
        if title_pos:
            m2 = _BLANK_TO_LINE.match(state.src, title_pos)
            if m2:
                title_pos = m2.end()
            else:
                title_pos = None
                title = None

        if title_pos is None:
            m3 = _BLANK_TO_LINE.match(state.src, href_pos)
            if m3:
                href_pos = m3.end()
            else:
                href_pos = None
                href = None

        end_pos = title_pos or href_pos
        if not end_pos:
            return None

        if key not in state.env["ref_links"]:
            assert href is not None
            href = unescape_char(href)
            data = {"url": escape_url(href), "label": label}
            if title:
                data["title"] = title
            state.env["ref_links"][key] = data
        return end_pos

    def extract_block_quote(self, m: Match[str], state: BlockState) -> Tuple[str, Optional[int]]:
        """Extract text and cursor end position of a block quote."""

        # cleanup at first to detect if it is code block
        text = m.group("quote_1") + "\n"
        text = expand_leading_tab(text, 3)
        text = _BLOCK_QUOTE_TRIM.sub("", text)

        sc = self.compile_sc(["blank_line", "indent_code", "fenced_code"])
        require_marker = bool(sc.match(text))

        state.cursor = m.end() + 1

        end_pos: Optional[int] = None
        if require_marker:
            m2 = _STRICT_BLOCK_QUOTE.match(state.src, state.cursor)
            if m2:
                quote = m2.group(0)
                quote = _BLOCK_QUOTE_LEADING.sub("", quote)
                quote = expand_leading_tab(quote, 3)
                quote = _BLOCK_QUOTE_TRIM.sub("", quote)
                text += quote
                state.cursor = m2.end()
        else:
            prev_blank_line = False
            break_sc = self.compile_sc(
                [
                    "blank_line",
                    "thematic_break",
                    "fenced_code",
                    "list",
                    "block_html",
                ]
            )
            while state.cursor < state.cursor_max:
                m3 = _STRICT_BLOCK_QUOTE.match(state.src, state.cursor)
                if m3:
                    quote = m3.group(0)
                    quote = _BLOCK_QUOTE_LEADING.sub("", quote)
                    quote = expand_leading_tab(quote, 3)
                    quote = _BLOCK_QUOTE_TRIM.sub("", quote)
                    text += quote
                    state.cursor = m3.end()
                    if not quote.strip():
                        prev_blank_line = True
                    else:
                        prev_blank_line = bool(_LINE_BLANK_END.search(quote))
                    continue

                if prev_blank_line:
```
