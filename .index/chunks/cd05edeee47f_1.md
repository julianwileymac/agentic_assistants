# Chunk: cd05edeee47f_1

- source: `.venv-lab/Lib/site-packages/cffi/_cffi_errors.h`
- lines: 102-150
- chunk: 2/2

```
    if (ecap == (PyObject *)1)
        return;

    if (ecap == NULL)
        goto error;

    s = PyRun_String("done()", Py_eval_input, ecap, ecap);
    if (s == NULL)
        goto error;

    /* Show a dialog box, but in a background thread, and
       never show multiple dialog boxes at once. */
#if PY_MAJOR_VERSION >= 3
    text = PyUnicode_AsWideCharString(s, NULL);
#else
    text = PyString_AsString(s);
#endif

    _cffi_bootstrap_text = text;

    if (text != NULL)
    {
        HANDLE h;
        h = CreateThread(NULL, 0, _cffi_bootstrap_dialog,
                         NULL, 0, NULL);
        if (h != NULL)
            CloseHandle(h);
    }
    /* decref the string, but it should stay alive as 'fl.buf'
       in the small module above.  It will really be freed only if
       we later get another similar error.  So it's a leak of at
       most one copy of the small module.  That's fine for this
       situation which is usually a "fatal error" anyway. */
    Py_DECREF(s);
    PyErr_Clear();
    return;

  error:
    _cffi_bootstrap_text = NULL;
    PyErr_Clear();
}

#else

static PyObject *_cffi_start_error_capture(void) { return NULL; }
static void _cffi_stop_error_capture(PyObject *ecap) { }

#endif
```
