# Chunk: d41d90eff3fc_1

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/contents/fileio.py`
- lines: 92-178
- chunk: 2/8

```
s by copying the previous file contents to a temporary file in the
    same directory, and renaming that file back to the target if the context
    exits with an error. If the context is successful, the new data is synced to
    disk and the temporary file is removed.

    Parameters
    ----------
    path : str
        The target file to write to.
    text : bool, optional
        Whether to open the file in text mode (i.e. to write unicode). Default is
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

    # Fall back to direct write for existing file in a non-writable dir
    dirpath = os.path.dirname(path) or os.getcwd()
    if os.path.isfile(path) and not os.access(dirpath, os.W_OK) and os.access(path, os.W_OK):
        mode = "w" if text else "wb"
        # direct open on the target file
        if text:
            fileobj = open(path, mode, encoding=encoding, **kwargs)  # noqa: SIM115
        else:
            fileobj = open(path, mode, **kwargs)  # noqa: SIM115
        try:
            yield fileobj
        finally:
            fileobj.close()
        return

    tmp_path = path_to_intermediate(path)

    if os.path.isfile(path):
        copy2_safe(path, tmp_path, log=log)

    if text:
        # Make sure that text files have Unix linefeeds by default
        kwargs.setdefault("newline", "\n")
        fileobj = open(path, "w", encoding=encoding, **kwargs)  # noqa: SIM115
    else:
        fileobj = open(path, "wb", **kwargs)  # noqa: SIM115

    try:
        yield fileobj
    except BaseException:
        # Failed! Move the backup file back to the real path to avoid corruption
        fileobj.close()
        replace_file(tmp_path, path)
        raise

    # Flush to disk
    fileobj.flush()
    os.fsync(fileobj.fileno())
    fileobj.close()

    # Written successfully, now remove the backup copy
    if os.path.isfile(tmp_path):
        os.remove(tmp_path)


@contextmanager
def _simple_writing(path, text=True, encoding="utf-8", log=None, **kwargs):
    """Context manager to write file without doing atomic writing
    (for weird filesystem eg: nfs).

    Parameters
    ----------
    path : str
        The target file to write to.
    text : bool, optional
        Whether to open the file in text mode (i.e. to write unicode). Default is
        True.
    encoding : str, optional
        The encoding to use for files opened in text mode. Default is UTF-8.
    **kwargs
        Passed to :func:`io.open`.
    """
    # realpath doesn't work on Windows: https://bugs.python.org/issue9949
```
