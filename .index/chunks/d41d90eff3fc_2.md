# Chunk: d41d90eff3fc_2

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/contents/fileio.py`
- lines: 170-252
- chunk: 3/8

```
 in text mode (i.e. to write unicode). Default is
        True.
    encoding : str, optional
        The encoding to use for files opened in text mode. Default is UTF-8.
    **kwargs
        Passed to :func:`io.open`.
    """
    # realpath doesn't work on Windows: https://bugs.python.org/issue9949
    # Luckily, we only need to resolve the file itself being a symlink, not
    # any of its directories, so this will suffice:
    if os.path.islink(path):
        path = os.path.join(os.path.dirname(path), os.readlink(path))

    if text:
        # Make sure that text files have Unix linefeeds by default
        kwargs.setdefault("newline", "\n")
        fileobj = open(path, "w", encoding=encoding, **kwargs)  # noqa: SIM115
    else:
        fileobj = open(path, "wb", **kwargs)  # noqa: SIM115

    try:
        yield fileobj
    except BaseException:
        fileobj.close()
        raise

    fileobj.close()


class FileManagerMixin(LoggingConfigurable, Configurable):
    """
    Mixin for ContentsAPI classes that interact with the filesystem.

    Provides facilities for reading, writing, and copying files.

    Shared by FileContentsManager and FileCheckpoints.

    Note
    ----
    Classes using this mixin must provide the following attributes:

    root_dir : unicode
        A directory against against which API-style paths are to be resolved.

    log : logging.Logger
    """

    use_atomic_writing = Bool(
        True,
        config=True,
        help="""By default notebooks are saved on disk on a temporary file and then if successfully written, it replaces the old ones.
      This procedure, namely 'atomic_writing', causes some bugs on file system without operation order enforcement (like some networked fs).
      If set to False, the new notebook is written directly on the old one which could fail (eg: full filesystem or quota )""",
    )

    hash_algorithm = Enum(  # type: ignore[call-overload]
        hashlib.algorithms_available,
        default_value="sha256",
        config=True,
        help="Hash algorithm to use for file content, support by hashlib",
    )

    @contextmanager
    def open(self, os_path, *args, **kwargs):
        """wrapper around io.open that turns permission errors into 403"""
        with self.perm_to_403(os_path), open(os_path, *args, **kwargs) as f:
            yield f

    @contextmanager
    def atomic_writing(self, os_path, *args, **kwargs):
        """wrapper around atomic_writing that turns permission errors to 403.
        Depending on flag 'use_atomic_writing', the wrapper perform an actual atomic writing or
        simply writes the file (whatever an old exists or not)"""
        with self.perm_to_403(os_path):
            kwargs["log"] = self.log
            if self.use_atomic_writing:
                with atomic_writing(os_path, *args, **kwargs) as f:
                    yield f
            else:
                with _simple_writing(os_path, *args, **kwargs) as f:
                    yield f
```
