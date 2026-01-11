# Chunk: 79e98be9acef_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/common/py_custom_pyeval_settrace.hpp`
- lines: 1-67
- chunk: 1/4

```
#ifndef _PY_CUSTOM_PYEVAL_SETTRACE_HPP_
#define _PY_CUSTOM_PYEVAL_SETTRACE_HPP_

#include "python.h"
#include "py_utils.hpp"
#include "py_custom_pyeval_settrace_common.hpp"
#include "py_custom_pyeval_settrace_310.hpp"
#include "py_custom_pyeval_settrace_311.hpp"

// On Python 3.7 onwards the thread state is not kept in PyThread_set_key_value (rather
// it uses PyThread_tss_set using PyThread_tss_set(&_PyRuntime.gilstate.autoTSSkey, (void *)tstate)
// and we don't have access to that key from here (thus, we can't use the previous approach which
// made CPython think that the current thread had the thread state where we wanted to set the tracing).
//
// So, the solution implemented here is not faking that change and reimplementing PyEval_SetTrace.
// The implementation is mostly the same from the one in CPython, but we have one shortcoming:
//
// When CPython sets the tracing for a thread it increments _Py_TracingPossible (actually
// _PyRuntime.ceval.tracing_possible). This implementation has one issue: it only works on
// deltas when the tracing is set (so, a settrace(func) will increase the _Py_TracingPossible global value and a
// settrace(None) will decrease it, but when a thread dies it's kept as is and is not decreased).
// -- as we don't currently have access to _PyRuntime we have to create a thread, set the tracing
// and let it die so that the count is increased (this is really hacky, but better than having
// to create a local copy of the whole _PyRuntime (defined in pystate.h with several inner structs)
// which would need to be kept up to date for each new CPython version just to increment that variable).



/**
 * This version is used in internalInitializeCustomPyEvalSetTrace->pyObject_FastCallDict on older
 * versions of CPython (pre 3.7).
 */
 static PyObject *
 PyObject_FastCallDictCustom(PyObject* callback, PyObject *stack[3], int ignoredStackSizeAlways3, void* ignored)
 {
     PyObject *args = internalInitializeCustomPyEvalSetTrace->pyTuple_New(3);
     PyObject *result;

      if (args == NULL) {
          return NULL;
      }

     IncRef(stack[0]);
     IncRef(stack[1]);
     IncRef(stack[2]);

    // I.e.: same thing as: PyTuple_SET_ITEM(args, 0, stack[0]);
    reinterpret_cast<PyTupleObject *>(args)->ob_item[0] = stack[0];
    reinterpret_cast<PyTupleObject *>(args)->ob_item[1] = stack[1];
    reinterpret_cast<PyTupleObject *>(args)->ob_item[2] = stack[2];

     /* call the Python-level function */
     result = internalInitializeCustomPyEvalSetTrace->pyEval_CallObjectWithKeywords(callback, args, (PyObject*)NULL);

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

```
