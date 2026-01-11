# Chunk: 8ade7dbb48a6_5

- source: `.venv-lab/Lib/site-packages/IPython/core/magic.py`
- lines: 392-467
- chunk: 6/11

```
 auto_status(self):
        """Return descriptive string with automagic status."""
        return self._auto_status[self.auto_magic]

    def lsmagic(self):
        """Return a dict of currently available magic functions.

        The return dict has the keys 'line' and 'cell', corresponding to the
        two types of magics we support.  Each value is a list of names.
        """
        return self.magics

    def lsmagic_docs(self, brief=False, missing=""):
        """Return dict of documentation of magic functions.

        The return dict has the keys 'line' and 'cell', corresponding to the
        two types of magics we support. Each value is a dict keyed by magic
        name whose value is the function docstring. If a docstring is
        unavailable, the value of `missing` is used instead.

        If brief is True, only the first line of each docstring will be returned.
        """
        docs = {}
        for m_type in self.magics:
            m_docs = {}
            for m_name, m_func in self.magics[m_type].items():
                if m_func.__doc__:
                    if brief:
                        m_docs[m_name] = m_func.__doc__.split("\n", 1)[0]
                    else:
                        m_docs[m_name] = m_func.__doc__.rstrip()
                else:
                    m_docs[m_name] = missing
            docs[m_type] = m_docs
        return docs

    def register_lazy(self, name: str, fully_qualified_name: str) -> None:
        """
        Lazily register a magic via an extension.


        Parameters
        ----------
        name : str
            Name of the magic you wish to register.
        fully_qualified_name :
            Fully qualified name of the module/submodule that should be loaded
            as an extensions when the magic is first called.
            It is assumed that loading this extensions will register the given
            magic.
        """

        self.lazy_magics[name] = fully_qualified_name

    def register(self, *magic_objects):
        """Register one or more instances of Magics.

        Take one or more classes or instances of classes that subclass the main
        `core.Magic` class, and register them with IPython to use the magic
        functions they provide.  The registration process will then ensure that
        any methods that have decorated to provide line and/or cell magics will
        be recognized with the `%x`/`%%x` syntax as a line/cell magic
        respectively.

        If classes are given, they will be instantiated with the default
        constructor.  If your classes need a custom constructor, you should
        instanitate them first and pass the instance.

        The provided arguments can be an arbitrary mix of classes and instances.

        Parameters
        ----------
        *magic_objects : one or more classes or instances
        """
        # Start by validating them to ensure they have all had their magic
```
