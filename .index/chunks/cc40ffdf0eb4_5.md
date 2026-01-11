# Chunk: cc40ffdf0eb4_5

- source: `.venv-lab/Lib/site-packages/mistune/block_parser.py`
- lines: 408-497
- chunk: 6/7

```
      # rule 4
        if marker.startswith("<!"):
            return _parse_html_to_end(state, ">", m.end())

        close_tag = None
        open_tag = None
        if marker.startswith("</"):
            close_tag = marker[2:].lower()
            # rule 6
            if close_tag in BLOCK_TAGS:
                return _parse_html_to_newline(state, self.BLANK_LINE)
        else:
            open_tag = marker[1:].lower()
            # rule 1
            if open_tag in PRE_TAGS:
                end_tag = "</" + open_tag + ">"
                return _parse_html_to_end(state, end_tag, m.end())
            # rule 6
            if open_tag in BLOCK_TAGS:
                return _parse_html_to_newline(state, self.BLANK_LINE)

        # Blocks of type 7 may not interrupt a paragraph.
        end_pos = state.append_paragraph()
        if end_pos:
            return end_pos

        # rule 7
        start_pos = m.end()
        end_pos = state.find_line_end()
        if (open_tag and _OPEN_TAG_END.match(state.src, start_pos, end_pos)) or (
            close_tag and _CLOSE_TAG_END.match(state.src, start_pos, end_pos)
        ):
            return _parse_html_to_newline(state, self.BLANK_LINE)

        return None

    def parse(self, state: BlockState, rules: Optional[List[str]] = None) -> None:
        sc = self.compile_sc(rules)

        while state.cursor < state.cursor_max:
            m = sc.search(state.src, state.cursor)
            if not m:
                break

            end_pos = m.start()
            if end_pos > state.cursor:
                text = state.get_text(end_pos)
                state.add_paragraph(text)
                state.cursor = end_pos

            end_pos2 = self.parse_method(m, state)
            if end_pos2:
                state.cursor = end_pos2
            else:
                end_pos3 = state.find_line_end()
                text = state.get_text(end_pos3)
                state.add_paragraph(text)
                state.cursor = end_pos3

        if state.cursor < state.cursor_max:
            text = state.src[state.cursor :]
            state.add_paragraph(text)
            state.cursor = state.cursor_max


def _parse_html_to_end(state: BlockState, end_marker: str, start_pos: int) -> int:
    marker_pos = state.src.find(end_marker, start_pos)
    if marker_pos == -1:
        text = state.src[state.cursor :]
        end_pos = state.cursor_max
    else:
        text = state.get_text(marker_pos)
        state.cursor = marker_pos
        end_pos = state.find_line_end()
        text += state.get_text(end_pos)

    state.append_token({"type": "block_html", "raw": text})
    return end_pos


def _parse_html_to_newline(state: BlockState, newline: Pattern[str]) -> int:
    m = newline.search(state.src, state.cursor)
    if m:
        end_pos = m.start()
        text = state.get_text(end_pos)
    else:
        text = state.src[state.cursor :]
        end_pos = state.cursor_max
```
