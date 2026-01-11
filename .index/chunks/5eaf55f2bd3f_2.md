# Chunk: 5eaf55f2bd3f_2

- source: `.venv-lab/Lib/site-packages/IPython/core/doctb.py`
- lines: 174-243
- chunk: 3/6

```
KeyError:
                # This happens in situations like errors inside generator
                # expressions, where local variables are listed in the
                # line, but can't be extracted from the frame.  I'm not
                # 100% sure this isn't actually a bug in inspect itself,
                # but since there's no info for us to compute with, the
                # best we can do is report the failure and move on.  Here
                # we must *not* call any traceback construction again,
                # because that would mess up use of %debug later on.  So we
                # simply report the failure and move on.  The only
                # limitation will be that this frame won't have locals
                # listed in the call signature.  Quite subtle problem...
                # I can't think of a good way to validate this in a unit
                # test, but running a script consisting of:
                #  dict( (k,v.strip()) for (k,v) in range(10) )
                # will illustrate the error, if this exception catch is
                # disabled.
                call = theme_table[self._theme_name].format(
                    [
                        (Token, "in "),
                        (Token.VName, func),
                        (Token.ValEm, "(***failed resolving arguments***)"),
                    ]
                )

        lvals_toks: list[TokenStream] = []
        if self.include_vars:
            try:
                # we likely want to fix stackdata at some point, but
                # still need a workaround.
                fibp = frame_info.variables_in_executing_piece
                for var in fibp:
                    lvals_toks.append(
                        [
                            (Token, var.name),
                            (Token, " "),
                            (Token.ValEm, "= "),
                            (Token.ValEm, repr(var.value)),
                        ]
                    )
            except Exception:
                lvals_toks.append(
                    [
                        (
                            Token,
                            "Exception trying to inspect frame. No more locals available.",
                        ),
                    ]
                )

        assert frame_info._sd is not None
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

    def prepare_header(self, etype: str) -> str:
        width = min(75, get_terminal_size()[0])
        head = theme_table[self._theme_name].format(
```
