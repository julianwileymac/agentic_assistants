# Chunk: 8ade7dbb48a6_6

- source: `.venv-lab/Lib/site-packages/IPython/core/magic.py`
- lines: 458-534
- chunk: 7/11

```
them first and pass the instance.

        The provided arguments can be an arbitrary mix of classes and instances.

        Parameters
        ----------
        *magic_objects : one or more classes or instances
        """
        # Start by validating them to ensure they have all had their magic
        # methods registered at the instance level
        for m in magic_objects:
            if not m.registered:
                raise ValueError(
                    "Class of magics %r was constructed without "
                    "the @register_magics class decorator"
                )
            if isinstance(m, type):
                # If we're given an uninstantiated class
                m = m(shell=self.shell)

            # Now that we have an instance, we can register it and update the
            # table of callables
            self.registry[m.__class__.__name__] = m
            for mtype in magic_kinds:
                self.magics[mtype].update(m.magics[mtype])

    def register_function(self, func, magic_kind="line", magic_name=None):
        """Expose a standalone function as magic function for IPython.

        This will create an IPython magic (line, cell or both) from a
        standalone function.  The functions should have the following
        signatures:

        * For line magics: `def f(line)`
        * For cell magics: `def f(line, cell)`
        * For a function that does both: `def f(line, cell=None)`

        In the latter case, the function will be called with `cell==None` when
        invoked as `%f`, and with cell as a string when invoked as `%%f`.

        Parameters
        ----------
        func : callable
            Function to be registered as a magic.
        magic_kind : str
            Kind of magic, one of 'line', 'cell' or 'line_cell'
        magic_name : optional str
            If given, the name the magic will have in the IPython namespace.  By
            default, the name of the function itself is used.
        """

        # Create the new method in the user_magics and register it in the
        # global table
        validate_type(magic_kind)
        magic_name = func.__name__ if magic_name is None else magic_name
        setattr(self.user_magics, magic_name, func)
        record_magic(self.magics, magic_kind, magic_name, func)

    def register_alias(
        self, alias_name, magic_name, magic_kind="line", magic_params=None
    ):
        """Register an alias to a magic function.

        The alias is an instance of :class:`MagicAlias`, which holds the
        name and kind of the magic it should call. Binding is done at
        call time, so if the underlying magic function is changed the alias
        will call the new function.

        Parameters
        ----------
        alias_name : str
            The name of the magic to be registered.
        magic_name : str
            The name of an existing magic.
        magic_kind : str
            Kind of magic, one of 'line' or 'cell'
```
