# Chunk: cc40ffdf0eb4_6

- source: `.venv-lab/Lib/site-packages/mistune/block_parser.py`
- lines: 485-499
- chunk: 7/7

```
 end_pos


def _parse_html_to_newline(state: BlockState, newline: Pattern[str]) -> int:
    m = newline.search(state.src, state.cursor)
    if m:
        end_pos = m.start()
        text = state.get_text(end_pos)
    else:
        text = state.src[state.cursor :]
        end_pos = state.cursor_max

    state.append_token({"type": "block_html", "raw": text})
    return end_pos
```
