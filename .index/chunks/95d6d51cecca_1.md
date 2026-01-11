# Chunk: 95d6d51cecca_1

- source: `.venv-lab/Lib/site-packages/pip/_vendor/rich/bar.py`
- lines: 77-94
- chunk: 2/2

```
   body = FULL_BLOCK * body_bar_count
        if body_eights_count:
            body += END_BLOCK_ELEMENTS[body_eights_count]

        suffix = " " * (width - len(body))

        yield Segment(prefix + body[len(prefix) :] + suffix, self.style)
        yield Segment.line()

    def __rich_measure__(
        self, console: Console, options: ConsoleOptions
    ) -> Measurement:
        return (
            Measurement(self.width, self.width)
            if self.width is not None
            else Measurement(4, options.max_width)
        )
```
