# Chunk: 8ade7dbb48a6_7

- source: `.venv-lab/Lib/site-packages/IPython/core/magic.py`
- lines: 523-600
- chunk: 8/11

```
ias
        will call the new function.

        Parameters
        ----------
        alias_name : str
            The name of the magic to be registered.
        magic_name : str
            The name of an existing magic.
        magic_kind : str
            Kind of magic, one of 'line' or 'cell'
        """

        # `validate_type` is too permissive, as it allows 'line_cell'
        # which we do not handle.
        if magic_kind not in magic_kinds:
            raise ValueError(
                "magic_kind must be one of %s, %s given" % magic_kinds, magic_kind
            )

        alias = MagicAlias(self.shell, magic_name, magic_kind, magic_params)
        setattr(self.user_magics, alias_name, alias)
        record_magic(self.magics, magic_kind, alias_name, alias)


# Key base class that provides the central functionality for magics.


class Magics(Configurable):
    """Base class for implementing magic functions.

    Shell functions which can be reached as %function_name. All magic
    functions should accept a string, which they can parse for their own
    needs. This can make some functions easier to type, eg `%cd ../`
    vs. `%cd("../")`

    Classes providing magic functions need to subclass this class, and they
    MUST:

    - Use the method decorators `@line_magic` and `@cell_magic` to decorate
      individual methods as magic functions, AND

    - Use the class decorator `@magics_class` to ensure that the magic
      methods are properly registered at the instance level upon instance
      initialization.

    See :mod:`magic_functions` for examples of actual implementation classes.
    """

    # Dict holding all command-line options for each magic.
    options_table: dict[str, t.Any] = {}
    # Dict for the mapping of magic names to methods, set by class decorator
    magics: dict[str, t.Any] = {}
    # Flag to check that the class decorator was properly applied
    registered: bool = False
    # Instance of IPython shell
    shell: None | InteractiveShell = None

    def __init__(self, shell=None, **kwargs):
        if not (self.__class__.registered):
            raise ValueError(
                "Magics subclass without registration - "
                "did you forget to apply @magics_class?"
            )
        if shell is not None:
            if hasattr(shell, "configurables"):
                shell.configurables.append(self)
            if hasattr(shell, "config"):
                kwargs.setdefault("parent", shell)

        self.shell = shell
        self.options_table = {}
        # The method decorators are run when the instance doesn't exist yet, so
        # they can only record the names of the methods they are supposed to
        # grab.  Only now, that the instance exists, can we create the proper
        # mapping to bound methods.  So we read the info off the original names
        # table and replace each method name by the actual bound method.
```
