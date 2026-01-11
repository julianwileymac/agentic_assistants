# Chunk: 72cb71dffcc7_6

- source: `.venv-lab/Lib/site-packages/IPython/core/ultratb.py`
- lines: 436-517
- chunk: 7/18

```
:
            return "<unprintable %s object>" % type(value).__name__


_sentinel = object()
_default = "default"


# ----------------------------------------------------------------------------
class VerboseTB(TBTools):
    """A port of Ka-Ping Yee's cgitb.py module that outputs color text instead
    of HTML.  Requires inspect and pydoc.  Crazy, man.

    Modified version which optionally strips the topmost entries from the
    traceback, to be used with alternate interpreters (because their own code
    would appear in the traceback)."""

    tb_highlight = "bg:ansiyellow"
    tb_highlight_style = "default"

    _mode: str

    def __init__(
        self,
        # TODO: no default ?
        theme_name: str = _default,
        call_pdb: bool = False,
        ostream: Any = None,
        tb_offset: int = 0,
        long_header: bool = False,
        include_vars: bool = True,
        check_cache: Callable[[], None] | None = None,
        debugger_cls: type | None = None,
        *,
        color_scheme: Any = _sentinel,
    ):
        """Specify traceback offset, headers and color scheme.

        Define how many frames to drop from the tracebacks. Calling it with
        tb_offset=1 allows use of this handler in interpreters which will have
        their own code at the top of the traceback (VerboseTB will first
        remove that frame before printing the traceback info)."""
        if color_scheme is not _sentinel:
            assert isinstance(color_scheme, str)
            theme_name = color_scheme.lower()

            warnings.warn(
                "color_scheme is deprecated as of IPython 9.0 and replaced by "
                "theme_name (which should be lowercase). As you passed a "
                "color_scheme value I will try to see if I have corresponding "
                "theme.",
                stacklevel=2,
                category=DeprecationWarning,
            )

            if theme_name != _default:
                warnings.warn(
                    "You passed both `theme_name` and `color_scheme` "
                    "(deprecated) to VerboseTB constructor. `theme_name` will "
                    "be ignored for the time being.",
                    stacklevel=2,
                    category=DeprecationWarning,
                )

        if theme_name == _default:
            theme_name = "linux"

        assert isinstance(theme_name, str)
        super().__init__(
            theme_name=theme_name,
            call_pdb=call_pdb,
            ostream=ostream,
            debugger_cls=debugger_cls,
        )
        self.tb_offset = tb_offset
        self.long_header = long_header
        self.include_vars = include_vars
        # By default we use linecache.checkcache, but the user can provide a
        # different check_cache implementation.  This was formerly used by the
        # IPython kernel for interactive code, but is no longer necessary.
        if check_cache is None:
```
