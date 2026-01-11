# Chunk: 5eaf55f2bd3f_3

- source: `.venv-lab/Lib/site-packages/IPython/core/doctb.py`
- lines: 233-325
- chunk: 4/6

```
           theme_table[self._theme_name],
                self.has_colors,
                lvals_toks,
            )
        )
        return result

    def prepare_header(self, etype: str) -> str:
        width = min(75, get_terminal_size()[0])
        head = theme_table[self._theme_name].format(
            [
                (
                    Token,
                    "Traceback (most recent call last):",
                ),
                (Token, " "),
            ]
        )

        return head

    def format_exception(self, etype: Any, evalue: Any) -> Any:
        # Get (safely) a string form of the exception info
        try:
            etype_str, evalue_str = map(str, (etype, evalue))
        except:
            # User exception is improperly defined.
            etype, evalue = str, sys.exc_info()[:2]
            etype_str, evalue_str = map(str, (etype, evalue))

        # PEP-678 notes
        notes = getattr(evalue, "__notes__", [])
        if not isinstance(notes, Sequence) or isinstance(notes, (str, bytes)):
            notes = [_safe_string(notes, "__notes__", func=repr)]

        # ... and format it
        return [
            theme_table[self._theme_name].format(
                [(Token.ExcName, etype_str), (Token, ": "), (Token, evalue_str)]
            ),
            *(
                theme_table[self._theme_name].format([(Token, _safe_string(n, "note"))])
                for n in notes
            ),
        ]

    def format_exception_as_a_whole(
        self,
        etype: type,
        evalue: Optional[BaseException],
        etb: Optional[TracebackType],
        context: int,
        tb_offset: Optional[int],
    ) -> list[list[str]]:
        """Formats the header, traceback and exception message for a single exception.

        This may be called multiple times by Python 3 exception chaining
        (PEP 3134).
        """
        # some locals
        orig_etype = etype
        try:
            etype = etype.__name__  # type: ignore[assignment]
        except AttributeError:
            pass

        tb_offset = self.tb_offset if tb_offset is None else tb_offset
        assert isinstance(tb_offset, int)
        head = self.prepare_header(str(etype))
        assert context == 1, context
        records = self.get_records(etb, context, tb_offset) if etb else []

        frames = []
        skipped = 0
        nskipped = len(records) - 1
        frames.append(self.format_record(records[0]))
        if nskipped:
            frames.append(
                theme_table[self._theme_name].format(
                    [
                        (Token, "\n"),
                        (Token, "    "),
                        (Token, "[... %s skipped frames]" % nskipped),
                        (Token, "\n"),
                        (Token, "\n"),
                    ]
                )
            )

        formatted_exception = self.format_exception(etype, evalue)
        return [[head] + frames + formatted_exception]
```
