# Chunk: 8ade7dbb48a6_4

- source: `.venv-lab/Lib/site-packages/IPython/core/magic.py`
- lines: 315-400
- chunk: 5/11

```
ll")

# -----------------------------------------------------------------------------
# Core Magic classes
# -----------------------------------------------------------------------------


class MagicsManager(Configurable):
    """Object that handles all magic-related functionality for IPython."""

    # Non-configurable class attributes

    # A two-level dict, first keyed by magic type, then by magic function, and
    # holding the actual callable object as value.  This is the dict used for
    # magic function dispatch
    magics = Dict()
    lazy_magics = Dict(
        help="""
    Mapping from magic names to modules to load.

    This can be used in IPython/IPykernel configuration to declare lazy magics
    that will only be imported/registered on first use.

    For example::

        c.MagicsManager.lazy_magics = {
          "my_magic": "slow.to.import",
          "my_other_magic": "also.slow",
        }

    On first invocation of `%my_magic`, `%%my_magic`, `%%my_other_magic` or
    `%%my_other_magic`, the corresponding module will be loaded as an ipython
    extensions as if you had previously done `%load_ext ipython`.

    Magics names should be without percent(s) as magics can be both cell
    and line magics.

    Lazy loading happen relatively late in execution process, and
    complex extensions that manipulate Python/IPython internal state or global state
    might not support lazy loading.
    """
    ).tag(
        config=True,
    )

    # A registry of the original objects that we've been given holding magics.
    registry = Dict()

    shell = Instance(
        "IPython.core.interactiveshell.InteractiveShellABC", allow_none=True
    )

    auto_magic = Bool(
        True, help="Automatically call line magics without requiring explicit % prefix"
    ).tag(config=True)

    @observe("auto_magic")
    def _auto_magic_changed(self, change):
        assert self.shell is not None
        self.shell.automagic = change["new"]

    _auto_status = [
        "Automagic is OFF, % prefix IS needed for line magics.",
        "Automagic is ON, % prefix IS NOT needed for line magics.",
    ]

    user_magics = Instance("IPython.core.magics.UserMagics", allow_none=True)

    def __init__(self, shell=None, config=None, user_magics=None, **traits):
        super(MagicsManager, self).__init__(
            shell=shell, config=config, user_magics=user_magics, **traits
        )
        self.magics = dict(line={}, cell={})
        # Let's add the user_magics to the registry for uniformity, so *all*
        # registered magic containers can be found there.
        self.registry[user_magics.__class__.__name__] = user_magics

    def auto_status(self):
        """Return descriptive string with automagic status."""
        return self._auto_status[self.auto_magic]

    def lsmagic(self):
        """Return a dict of currently available magic functions.

        The return dict has the keys 'line' and 'cell', corresponding to the
```
