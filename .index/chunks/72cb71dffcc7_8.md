# Chunk: 72cb71dffcc7_8

- source: `.venv-lab/Lib/site-packages/IPython/core/ultratb.py`
- lines: 570-642
- chunk: 9/18

```
..
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

        if frame_info._sd is None:
            # fast fallback if file is too long
            assert frame_info.filename is not None
            level_tokens = [
                (Token.FilenameEm, util_path.compress_user(frame_info.filename)),
                (Token, " "),
                (Token, call),
                (Token, "\n"),
            ]

            _line_format = Parser(theme_name=self._theme_name).format2
            assert isinstance(frame_info.code, types.CodeType)
            first_line: int = frame_info.code.co_firstlineno
            current_line: int = frame_info.lineno
            raw_lines: list[str] = frame_info.raw_lines
            index: int = current_line - first_line
            assert frame_info.context is not None
            if index >= frame_info.context:
                start = max(index - frame_info.context, 0)
                stop = index + frame_info.context
                index = frame_info.context
            else:
                start = 0
                stop = index + frame_info.context
            raw_lines = raw_lines[start:stop]

            # Jan 2025: may need _line_format(py3ompat.cast_unicode(s))
            raw_color_err = []
            for s in raw_lines:
                formatted, is_error = _line_format(s, "str")
                assert formatted is not None, "format2 should return str when out='str'"
                raw_color_err.append((s, (formatted, is_error)))
```
