# Chunk: 6f3dcfe8cb9a_2

- source: `.venv-lab/Lib/site-packages/IPython/utils/_process_common.py`
- lines: 161-221
- chunk: 3/3

```
t_output_error_code(cmd):
    """Return (standard output, standard error, return code) of executing cmd
    in a shell.

    Accepts the same arguments as os.system().

    Parameters
    ----------
    cmd : str or list
        A command to be executed in the system shell.

    Returns
    -------
    stdout : str
    stderr : str
    returncode: int
    """

    out_err, p = process_handler(cmd, lambda p: (p.communicate(), p))
    if out_err is None:
        return '', '', p.returncode
    out, err = out_err
    return py3compat.decode(out), py3compat.decode(err), p.returncode

def arg_split(s, posix=False, strict=True):
    """Split a command line's arguments in a shell-like manner.

    This is a modified version of the standard library's shlex.split()
    function, but with a default of posix=False for splitting, so that quotes
    in inputs are respected.

    if strict=False, then any errors shlex.split would raise will result in the
    unparsed remainder being the last element of the list, rather than raising.
    This is because we sometimes use arg_split to parse things other than
    command-line args.
    """

    lex = shlex.shlex(s, posix=posix)
    lex.whitespace_split = True
    # Extract tokens, ensuring that things like leaving open quotes
    # does not cause this to raise.  This is important, because we
    # sometimes pass Python source through this (e.g. %timeit f(" ")),
    # and it shouldn't raise an exception.
    # It may be a bad idea to parse things that are not command-line args
    # through this function, but we do, so let's be safe about it.
    lex.commenters='' #fix for GH-1269
    tokens = []
    while True:
        try:
            tokens.append(next(lex))
        except StopIteration:
            break
        except ValueError:
            if strict:
                raise
            # couldn't parse, get remaining blob as last token
            tokens.append(lex.token)
            break

    return tokens
```
