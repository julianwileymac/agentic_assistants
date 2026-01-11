# Chunk: cc40ffdf0eb4_4

- source: `.venv-lab/Lib/site-packages/mistune/block_parser.py`
- lines: 331-418
- chunk: 5/7

```
                 state.cursor = m3.end()
                    if not quote.strip():
                        prev_blank_line = True
                    else:
                        prev_blank_line = bool(_LINE_BLANK_END.search(quote))
                    continue

                if prev_blank_line:
                    # CommonMark Example 249
                    # because of laziness, a blank line is needed between
                    # a block quote and a following paragraph
                    break

                m4 = break_sc.match(state.src, state.cursor)
                if m4:
                    end_pos = self.parse_method(m4, state)
                    if end_pos:
                        break

                # lazy continuation line
                pos = state.find_line_end()
                line = state.get_text(pos)
                line = expand_leading_tab(line, 3)
                text += line
                state.cursor = pos

        # according to CommonMark Example 6, the second tab should be
        # treated as 4 spaces
        return expand_tab(text), end_pos

    def parse_block_quote(self, m: Match[str], state: BlockState) -> int:
        """Parse token for block quote. Here is an example of the syntax:

        .. code-block:: markdown

            > a block quote starts
            > with right arrows
        """
        text, end_pos = self.extract_block_quote(m, state)
        # scan children state
        child = state.child_state(text)
        if state.depth() >= self.max_nested_level - 1:
            rules = list(self.block_quote_rules)
            rules.remove("block_quote")
        else:
            rules = self.block_quote_rules

        self.parse(child, rules)
        token = {"type": "block_quote", "children": child.tokens}
        if end_pos:
            state.prepend_token(token)
            return end_pos
        state.append_token(token)
        return state.cursor

    def parse_list(self, m: Match[str], state: BlockState) -> int:
        """Parse tokens for ordered and unordered list."""
        return parse_list(self, m, state)

    def parse_block_html(self, m: Match[str], state: BlockState) -> Optional[int]:
        return self.parse_raw_html(m, state)

    def parse_raw_html(self, m: Match[str], state: BlockState) -> Optional[int]:
        marker = m.group(0).strip()

        # rule 2
        if marker == "<!--":
            return _parse_html_to_end(state, "-->", m.end())

        # rule 3
        if marker == "<?":
            return _parse_html_to_end(state, "?>", m.end())

        # rule 5
        if marker == "<![CDATA[":
            return _parse_html_to_end(state, "]]>", m.end())

        # rule 4
        if marker.startswith("<!"):
            return _parse_html_to_end(state, ">", m.end())

        close_tag = None
        open_tag = None
        if marker.startswith("</"):
            close_tag = marker[2:].lower()
            # rule 6
            if close_tag in BLOCK_TAGS:
```
