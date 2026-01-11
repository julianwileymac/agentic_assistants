# Chunk: a83acd6ec9cf_3

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/input/vt100_parser.py`
- lines: 240-251
- chunk: 4/4

```
 timeout, and processes everything that's still in the buffer as-is, so
        without assuming any characters will follow.
        """
        self._input_parser.send(_Flush())

    def feed_and_flush(self, data: str) -> None:
        """
        Wrapper around ``feed`` and ``flush``.
        """
        self.feed(data)
        self.flush()
```
