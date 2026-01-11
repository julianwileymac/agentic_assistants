# Chunk: 72cb71dffcc7_3

- source: `.venv-lab/Lib/site-packages/IPython/core/ultratb.py`
- lines: 232-303
- chunk: 4/18

```
  evalue,
                    (etb, chained_exc_ids),  # type: ignore[arg-type]
                    chained_exceptions_tb_offset,
                    context,
                )
                ol2 = chained_exception_message

                out_list = ol1 + ol2 + out_list

        return out_list

    def _format_list(self, extracted_list: list[Any]) -> list[str]:
        """Format a list of traceback entry tuples for printing.

        Given a list of tuples as returned by extract_tb() or
        extract_stack(), return a list of strings ready for printing.
        Each string in the resulting list corresponds to the item with the
        same index in the argument list.  Each string ends in a newline;
        the strings may contain internal newlines as well, for those items
        whose source text line is not None.

        Lifted almost verbatim from traceback.py
        """

        output_list = []
        for ind, (filename, lineno, name, line) in enumerate(extracted_list):
            # Will emphasize the last entry
            em = True if ind == len(extracted_list) - 1 else False

            item = theme_table[self._theme_name].format(
                [(Token.NormalEm if em else Token.Normal, "  ")]
                + _tokens_filename(em, filename, lineno=lineno)
            )

            # This seem to be only in xmode plain (%run sinpleer), investigate why not share with verbose.
            # look at _tokens_filename in forma_record.
            if name != "<module>":
                item += theme_table[self._theme_name].format(
                    [
                        (Token.NormalEm if em else Token.Normal, " in "),
                        (Token.TB.NameEm if em else Token.TB.Name, name),
                    ]
                )
            item += theme_table[self._theme_name].format(
                [(Token.NormalEm if em else Token, "\n")]
            )
            if line:
                item += theme_table[self._theme_name].format(
                    [
                        (Token.Line if em else Token, "    "),
                        (Token.Line if em else Token, line.strip()),
                        (Token, "\n"),
                    ]
                )
            output_list.append(item)

        return output_list

    def _format_exception_only(
        self, etype: type[BaseException], value: BaseException | None
    ) -> list[str]:
        """Format the exception part of a traceback.

        The arguments are the exception type and value such as given by
        sys.exc_info()[:2]. The return value is a list of strings, each ending
        in a newline.  Normally, the list contains a single string; however,
        for SyntaxError exceptions, it contains several lines that (when
        printed) display detailed information about where the syntax error
        occurred.  The message indicating which exception occurred is the
        always last string in the list.
```
