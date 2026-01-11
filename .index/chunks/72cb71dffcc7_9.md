# Chunk: 72cb71dffcc7_9

- source: `.venv-lab/Lib/site-packages/IPython/core/ultratb.py`
- lines: 635-711
- chunk: 10/18

```
pat.cast_unicode(s))
            raw_color_err = []
            for s in raw_lines:
                formatted, is_error = _line_format(s, "str")
                assert formatted is not None, "format2 should return str when out='str'"
                raw_color_err.append((s, (formatted, is_error)))

            tb_tokens = _simple_format_traceback_lines(
                current_line,
                index,
                raw_color_err,
                lvals_toks,
                theme=theme_table[self._theme_name],
            )
            _tb_lines: str = theme_table[self._theme_name].format(tb_tokens)

            return theme_table[self._theme_name].format(level_tokens + tb_tokens)
        else:
            result = theme_table[self._theme_name].format(
                _tokens_filename(True, frame_info.filename, lineno=frame_info.lineno)
            )
            result += ", " if call else ""
            result += f"{call}\n"
            result += theme_table[self._theme_name].format(
                _format_traceback_lines(
                    frame_info.lines,
                    theme_table[self._theme_name],
                    self.has_colors,
                    lvals_toks,
                )
            )
            return result

    def prepare_header(self, etype: str, long_version: bool = False) -> str:
        width = min(75, get_terminal_size()[0])
        if long_version:
            # Header with the exception type, python version, and date
            pyver = "Python " + sys.version.split()[0] + ": " + sys.executable
            date = time.ctime(time.time())
            theme = theme_table[self._theme_name]
            head = theme.format(
                [
                    (Token.Topline, theme.symbols["top_line"] * width),
                    (Token, "\n"),
                    (Token.ExcName, etype),
                    (Token, " " * (width - len(etype) - len(pyver))),
                    (Token, pyver),
                    (Token, "\n"),
                    (Token, date.rjust(width)),
                ]
            )
            head += (
                "\nA problem occurred executing Python code.  Here is the sequence of function"
                "\ncalls leading up to the error, with the most recent (innermost) call last."
            )
        else:
            # Simplified header
            head = theme_table[self._theme_name].format(
                [
                    (Token.ExcName, etype),
                    (
                        Token,
                        "Traceback (most recent call last)".rjust(width - len(etype)),
                    ),
                ]
            )

        return head

    def format_exception(self, etype, evalue):
        # Get (safely) a string form of the exception info
        try:
            etype_str, evalue_str = map(str, (etype, evalue))
        except:
            # User exception is improperly defined.
            etype, evalue = str, sys.exc_info()[:2]
```
