# Chunk: cd05edeee47f_0

- source: `.venv-lab/Lib/site-packages/cffi/_cffi_errors.h`
- lines: 1-114
- chunk: 1/2

```
#ifndef CFFI_MESSAGEBOX
# ifdef _MSC_VER
#  define CFFI_MESSAGEBOX  1
# else
#  define CFFI_MESSAGEBOX  0
# endif
#endif


#if CFFI_MESSAGEBOX
/* Windows only: logic to take the Python-CFFI embedding logic
   initialization errors and display them in a background thread
   with MessageBox.  The idea is that if the whole program closes
   as a result of this problem, then likely it is already a console
   program and you can read the stderr output in the console too.
   If it is not a console program, then it will likely show its own
   dialog to complain, or generally not abruptly close, and for this
   case the background thread should stay alive.
*/
static void *volatile _cffi_bootstrap_text;

static PyObject *_cffi_start_error_capture(void)
{
    PyObject *result = NULL;
    PyObject *x, *m, *bi;

    if (InterlockedCompareExchangePointer(&_cffi_bootstrap_text,
            (void *)1, NULL) != NULL)
        return (PyObject *)1;

    m = PyImport_AddModule("_cffi_error_capture");
    if (m == NULL)
        goto error;

    result = PyModule_GetDict(m);
    if (result == NULL)
        goto error;

#if PY_MAJOR_VERSION >= 3
    bi = PyImport_ImportModule("builtins");
#else
    bi = PyImport_ImportModule("__builtin__");
#endif
    if (bi == NULL)
        goto error;
    PyDict_SetItemString(result, "__builtins__", bi);
    Py_DECREF(bi);

    x = PyRun_String(
        "import sys\n"
        "class FileLike:\n"
        "  def write(self, x):\n"
        "    try:\n"
        "      of.write(x)\n"
        "    except: pass\n"
        "    self.buf += x\n"
        "  def flush(self):\n"
        "    pass\n"
        "fl = FileLike()\n"
        "fl.buf = ''\n"
        "of = sys.stderr\n"
        "sys.stderr = fl\n"
        "def done():\n"
        "  sys.stderr = of\n"
        "  return fl.buf\n",   /* make sure the returned value stays alive */
        Py_file_input,
        result, result);
    Py_XDECREF(x);

 error:
    if (PyErr_Occurred())
    {
        PyErr_WriteUnraisable(Py_None);
        PyErr_Clear();
    }
    return result;
}

#pragma comment(lib, "user32.lib")

static DWORD WINAPI _cffi_bootstrap_dialog(LPVOID ignored)
{
    Sleep(666);    /* may be interrupted if the whole process is closing */
#if PY_MAJOR_VERSION >= 3
    MessageBoxW(NULL, (wchar_t *)_cffi_bootstrap_text,
                L"Python-CFFI error",
                MB_OK | MB_ICONERROR);
#else
    MessageBoxA(NULL, (char *)_cffi_bootstrap_text,
                "Python-CFFI error",
                MB_OK | MB_ICONERROR);
#endif
    _cffi_bootstrap_text = NULL;
    return 0;
}

static void _cffi_stop_error_capture(PyObject *ecap)
{
    PyObject *s;
    void *text;

    if (ecap == (PyObject *)1)
        return;

    if (ecap == NULL)
        goto error;

    s = PyRun_String("done()", Py_eval_input, ecap, ecap);
    if (s == NULL)
        goto error;

    /* Show a dialog box, but in a background thread, and
       never show multiple dialog boxes at once. */
```
