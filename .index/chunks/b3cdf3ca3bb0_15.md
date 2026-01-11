# Chunk: b3cdf3ca3bb0_15

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/document.py`
- lines: 1172-1183
- chunk: 16/16

```
onState(
                original_cursor_position=selection_state.original_cursor_position
                + len(text),
                type=selection_state.type,
            )

        return Document(
            text=text + self.text,
            cursor_position=self.cursor_position + len(text),
            selection=selection_state,
        )
```
