# Chunk: 2ffdc68c31bc_1

- source: `.venv-lab/Lib/site-packages/IPython/utils/encoding.py`
- lines: 71-93
- chunk: 2/2

```
     try:
            # There are reports of getpreferredencoding raising errors
            # in some cases, which may well be fixed, but let's be conservative here.
            enc = locale.getpreferredencoding()
        except Exception:
            pass
    enc = enc or sys.getdefaultencoding()
    # On windows `cp0` can be returned to indicate that there is no code page.
    # Since cp0 is an invalid encoding return instead cp1252 which is the
    # Western European default.
    if enc == "cp0":
        warnings.warn(
            "Invalid code page cp0 detected - using cp1252 instead."
            "If cp1252 is incorrect please ensure a valid code page "
            "is defined for the process.",
            RuntimeWarning,
        )
        return "cp1252"
    return enc


DEFAULT_ENCODING = getdefaultencoding()
```
