# Chunk: aca6aad60b48_1

- source: `.venv-lab/Lib/site-packages/IPython/utils/io.py`
- lines: 91-136
- chunk: 2/2

```
 loops.

    Valid answers are: y/yes/n/no (match is not case sensitive)."""

    answers = {'y':True,'n':False,'yes':True,'no':False}
    ans = None
    while ans not in answers.keys():
        try:
            ans = input(prompt+' ').lower()
            if not ans:  # response was an empty string
                ans = default
        except KeyboardInterrupt:
            if interrupt:
                ans = interrupt
            print("\r")
        except EOFError:
            if default in answers.keys():
                ans = default
                print()
            else:
                raise

    return answers[ans]


def temp_pyfile(src, ext='.py'):
    """Make a temporary python file, return filename and filehandle.

    Parameters
    ----------
    src : string or list of strings (no need for ending newlines if list)
        Source code to be written to the file.
    ext : optional, string
        Extension for the generated file.

    Returns
    -------
    (filename, open filehandle)
        It is the caller's responsibility to close the open file and unlink it.
    """
    fname = tempfile.mkstemp(ext)[1]
    with open(Path(fname), "w", encoding="utf-8") as f:
        f.write(src)
        f.flush()
    return fname
```
