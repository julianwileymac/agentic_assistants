# Chunk: afab4fb70a3a_1

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/formatted_text/utils.py`
- lines: 96-103
- chunk: 2/2

```
t(OneStyleAndTextTuple, (style, parts[-1], *mouse_handler)))

    # Always yield the last line, even when this is an empty line. This ensures
    # that when `fragments` ends with a newline character, an additional empty
    # line is yielded. (Otherwise, there's no way to differentiate between the
    # cases where `fragments` does and doesn't end with a newline.)
    yield line
```
