# Chunk: 72cb71dffcc7_2

- source: `.venv-lab/Lib/site-packages/IPython/core/ultratb.py`
- lines: 166-243
- chunk: 3/18

```
a stored in the exception
        etb : list | TracebackType | None
            If list: List of frames, see class docstring for details.
            If Traceback: Traceback of the exception.
        tb_offset : int, optional
            Number of frames in the traceback to skip.  If not given, the
            instance evalue is used (set in constructor).
        context : int, optional
            Number of lines of context information to print.

        Returns
        -------
        String with formatted exception.
        """
        # This is a workaround to get chained_exc_ids in recursive calls
        # etb should not be a tuple if structured_traceback is not recursive
        if isinstance(etb, tuple):
            etb, chained_exc_ids = etb
        else:
            chained_exc_ids = set()
        elist: list[Any]
        if isinstance(etb, list):
            elist = etb
        elif etb is not None:
            elist = self._extract_tb(etb)  # type: ignore[assignment]
        else:
            elist = []
        tb_offset = self.tb_offset if tb_offset is None else tb_offset
        assert isinstance(tb_offset, int)
        out_list: list[str] = []
        if elist:
            if tb_offset and len(elist) > tb_offset:
                elist = elist[tb_offset:]

            out_list.append(
                theme_table[self._theme_name].format(
                    [
                        (Token, "Traceback"),
                        (Token, " "),
                        (Token.NormalEm, "(most recent call last)"),
                        (Token, ":"),
                        (Token, "\n"),
                    ]
                ),
            )
            out_list.extend(self._format_list(elist))
        # The exception info should be a single entry in the list.
        lines = "".join(self._format_exception_only(etype, evalue))
        out_list.append(lines)

        # Find chained exceptions if we have a traceback (not for exception-only mode)
        if etb is not None:
            exception = self.get_parts_of_chained_exception(evalue)

            if exception and (id(exception[1]) not in chained_exc_ids):
                chained_exception_message: list[str] = (
                    self.prepare_chained_exception_message(evalue.__cause__)[0]
                    if evalue is not None
                    else [""]
                )
                etype, evalue, etb = exception
                # Trace exception to avoid infinite 'cause' loop
                chained_exc_ids.add(id(exception[1]))
                chained_exceptions_tb_offset = 0
                ol1 = self.structured_traceback(
                    etype,
                    evalue,
                    (etb, chained_exc_ids),  # type: ignore[arg-type]
                    chained_exceptions_tb_offset,
                    context,
                )
                ol2 = chained_exception_message

                out_list = ol1 + ol2 + out_list

        return out_list
```
