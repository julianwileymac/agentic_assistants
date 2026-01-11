# Chunk: 79e98be9acef_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/common/py_custom_pyeval_settrace.hpp`
- lines: 55-133
- chunk: 2/4

```
  /* cleanup */
    DecRef(args, internalInitializeCustomPyEvalSetTrace->isDebug);
    return result;
}

static PyObject *
InternalCallTrampoline(PyObject* callback,
                PyFrameObjectBaseUpTo39 *frame, int what, PyObject *arg)
{
    PyObject *result;
    PyObject *stack[3];

// Note: this is commented out from CPython (we shouldn't need it and it adds a reasonable overhead).
//     if (PyFrame_FastToLocalsWithError(frame) < 0) {
//         return NULL;
//     }
//
    stack[0] = (PyObject *)frame;
    stack[1] = InternalWhatstrings_37[what];
    stack[2] = (arg != NULL) ? arg : internalInitializeCustomPyEvalSetTrace->pyNone;
    
    
    // Helpers to print info.
    // printf("%s\n", internalInitializeCustomPyEvalSetTrace->pyUnicode_AsUTF8(internalInitializeCustomPyEvalSetTrace->pyObject_Repr((PyObject *)stack[0])));
    // printf("%s\n", internalInitializeCustomPyEvalSetTrace->pyUnicode_AsUTF8(internalInitializeCustomPyEvalSetTrace->pyObject_Repr((PyObject *)stack[1])));
    // printf("%s\n", internalInitializeCustomPyEvalSetTrace->pyUnicode_AsUTF8(internalInitializeCustomPyEvalSetTrace->pyObject_Repr((PyObject *)stack[2])));
    // printf("%s\n", internalInitializeCustomPyEvalSetTrace->pyUnicode_AsUTF8(internalInitializeCustomPyEvalSetTrace->pyObject_Repr((PyObject *)callback)));

    // call the Python-level function
    // result = _PyObject_FastCall(callback, stack, 3);
    //
    // Note that _PyObject_FastCall is actually a define:
    // #define _PyObject_FastCall(func, args, nargs) _PyObject_FastCallDict((func), (args), (nargs), NULL)

    result = internalInitializeCustomPyEvalSetTrace->pyObject_FastCallDict(callback, stack, 3, NULL);


// Note: this is commented out from CPython (we shouldn't need it and it adds a reasonable overhead).
//     PyFrame_LocalsToFast(frame, 1);

    if (result == NULL) {
        internalInitializeCustomPyEvalSetTrace->pyTraceBack_Here(frame);
    }

    return result;
}

static int
InternalTraceTrampoline(PyObject *self, PyFrameObject *frameParam,
                 int what, PyObject *arg)
{
    PyObject *callback;
    PyObject *result;
    
    PyFrameObjectBaseUpTo39 *frame = reinterpret_cast<PyFrameObjectBaseUpTo39*>(frameParam);

    if (what == PyTrace_CALL){
        callback = self;
    } else {
        callback = frame->f_trace;
    }

    if (callback == NULL){
        return 0;
    }

    result = InternalCallTrampoline(callback, frame, what, arg);
    if (result == NULL) {
        // Note: calling the original sys.settrace here.
        internalInitializeCustomPyEvalSetTrace->pyEval_SetTrace(NULL, NULL);
        PyObject *temp_f_trace = frame->f_trace;
        frame->f_trace = NULL;
        if(temp_f_trace != NULL){
            DecRef(temp_f_trace, internalInitializeCustomPyEvalSetTrace->isDebug);
        }
        return -1;
    }
    if (result != internalInitializeCustomPyEvalSetTrace->pyNone) {
```
