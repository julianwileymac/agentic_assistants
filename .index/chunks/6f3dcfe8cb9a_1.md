# Chunk: 6f3dcfe8cb9a_1

- source: `.venv-lab/Lib/site-packages/IPython/utils/_process_common.py`
- lines: 71-174
- chunk: 2/3

```
urn value of the provided callback is returned.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    # On win32, close_fds can't be true when using pipes for stdin/out/err
    if sys.platform == "win32" and stderr != subprocess.PIPE:
        close_fds = False
    else:
        close_fds = True
    # Determine if cmd should be run with system shell.
    shell = isinstance(cmd, str)
    # On POSIX systems run shell commands with user-preferred shell.
    executable = None
    if shell and os.name == 'posix' and 'SHELL' in os.environ:
        executable = os.environ['SHELL']
    p = subprocess.Popen(cmd, shell=shell,
                         executable=executable,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=stderr,
                         close_fds=close_fds)

    try:
        out = callback(p)
    except KeyboardInterrupt:
        print('^C')
        sys.stdout.flush()
        sys.stderr.flush()
        out = None
    finally:
        # Make really sure that we don't leave processes behind, in case the
        # call above raises an exception
        # We start by assuming the subprocess finished (to avoid NameErrors
        # later depending on the path taken)
        if p.returncode is None:
            try:
                p.terminate()
                p.poll()
            except OSError:
                pass
        # One last try on our way out
        if p.returncode is None:
            try:
                p.kill()
            except OSError:
                pass

    return out


def getoutput(cmd):
    """Run a command and return its stdout/stderr as a string.

    Parameters
    ----------
    cmd : str or list
        A command to be executed in the system shell.

    Returns
    -------
    output : str
        A string containing the combination of stdout and stderr from the
    subprocess, in whatever order the subprocess originally wrote to its
    file descriptors (so the order of the information in this string is the
    correct order as would be seen if running the command in a terminal).
    """
    out = process_handler(cmd, lambda p: p.communicate()[0], subprocess.STDOUT)
    if out is None:
        return ''
    assert isinstance(out, bytes)
    return py3compat.decode(out)


def getoutputerror(cmd):
    """Return (standard output, standard error) of executing cmd in a shell.

    Accepts the same arguments as os.system().

    Parameters
    ----------
    cmd : str or list
        A command to be executed in the system shell.

    Returns
    -------
    stdout : str
    stderr : str
    """
    return get_output_error_code(cmd)[:2]

def get_output_error_code(cmd):
    """Return (standard output, standard error, return code) of executing cmd
    in a shell.

    Accepts the same arguments as os.system().

    Parameters
    ----------
    cmd : str or list
        A command to be executed in the system shell.

    Returns
    -------
```
