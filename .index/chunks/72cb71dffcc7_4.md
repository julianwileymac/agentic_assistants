# Chunk: 72cb71dffcc7_4

- source: `.venv-lab/Lib/site-packages/IPython/core/ultratb.py`
- lines: 297-367
- chunk: 5/18

```
t contains a single string; however,
        for SyntaxError exceptions, it contains several lines that (when
        printed) display detailed information about where the syntax error
        occurred.  The message indicating which exception occurred is the
        always last string in the list.

        Also lifted nearly verbatim from traceback.py
        """
        have_filedata = False
        output_list = []
        stype_tokens = [(Token.ExcName, etype.__name__)]
        stype: str = theme_table[self._theme_name].format(stype_tokens)
        if value is None:
            # Not sure if this can still happen in Python 2.6 and above
            output_list.append(stype + "\n")
        else:
            if issubclass(etype, SyntaxError):
                assert hasattr(value, "filename")
                assert hasattr(value, "lineno")
                assert hasattr(value, "text")
                assert hasattr(value, "offset")
                assert hasattr(value, "msg")
                have_filedata = True
                if not value.filename:
                    value.filename = "<string>"
                if value.lineno:
                    lineno = value.lineno
                    textline = linecache.getline(value.filename, value.lineno)
                else:
                    lineno = "unknown"
                    textline = ""
                output_list.append(
                    theme_table[self._theme_name].format(
                        [(Token, "  ")]
                        + _tokens_filename(
                            True,
                            value.filename,
                            lineno=(None if lineno == "unknown" else lineno),
                        )
                        + [(Token, "\n")]
                    )
                )
                if textline == "":
                    # sep 2025:
                    # textline = py3compat.cast_unicode(value.text, "utf-8")
                    if value.text is None:
                        textline = ""
                    else:
                        assert isinstance(value.text, str)
                        textline = value.text

                if textline is not None:
                    i = 0
                    while i < len(textline) and textline[i].isspace():
                        i += 1
                    output_list.append(
                        theme_table[self._theme_name].format(
                            [
                                (Token.Line, "    "),
                                (Token.Line, textline.strip()),
                                (Token, "\n"),
                            ]
                        )
                    )
                    if value.offset is not None:
                        s = "    "
                        for c in textline[i : value.offset - 1]:
                            if c.isspace():
                                s += c
                            else:
```
