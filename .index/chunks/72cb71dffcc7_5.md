# Chunk: 72cb71dffcc7_5

- source: `.venv-lab/Lib/site-packages/IPython/core/ultratb.py`
- lines: 359-447
- chunk: 6/18

```
          )
                    )
                    if value.offset is not None:
                        s = "    "
                        for c in textline[i : value.offset - 1]:
                            if c.isspace():
                                s += c
                            else:
                                s += " "
                        output_list.append(
                            theme_table[self._theme_name].format(
                                [(Token.Caret, s + "^"), (Token, "\n")]
                            )
                        )
                s = value.msg
            else:
                s = self._some_str(value)
            if s:
                output_list.append(
                    theme_table[self._theme_name].format(
                        stype_tokens
                        + [
                            (Token.ExcName, ":"),
                            (Token, " "),
                            (Token, s),
                            (Token, "\n"),
                        ]
                    )
                )
            else:
                output_list.append("%s\n" % stype)

            # PEP-678 notes
            output_list.extend(f"{x}\n" for x in getattr(value, "__notes__", []))

        # sync with user hooks
        if have_filedata:
            ipinst = get_ipython()
            if ipinst is not None:
                assert value is not None
                assert hasattr(value, "lineno")
                assert hasattr(value, "filename")
                ipinst.hooks.synchronize_with_editor(value.filename, value.lineno, 0)

        return output_list

    def get_exception_only(self, etype, value):
        """Only print the exception type and message, without a traceback.

        Parameters
        ----------
        etype : exception type
        value : exception value
        """
        return ListTB.structured_traceback(self, etype, value)

    def show_exception_only(
        self, etype: BaseException | None, evalue: TracebackType | None
    ) -> None:
        """Only print the exception type and message, without a traceback.

        Parameters
        ----------
        etype : exception type
        evalue : exception value
        """
        # This method needs to use __call__ from *this* class, not the one from
        # a subclass whose signature or behavior may be different
        ostream = self.ostream
        ostream.flush()
        ostream.write("\n".join(self.get_exception_only(etype, evalue)))
        ostream.flush()

    def _some_str(self, value: Any) -> str:
        # Lifted from traceback.py
        try:
            return str(value)
        except:
            return "<unprintable %s object>" % type(value).__name__


_sentinel = object()
_default = "default"


# ----------------------------------------------------------------------------
class VerboseTB(TBTools):
    """A port of Ka-Ping Yee's cgitb.py module that outputs color text instead
```
