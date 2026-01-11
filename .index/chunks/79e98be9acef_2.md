# Chunk: 79e98be9acef_2

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/common/py_custom_pyeval_settrace.hpp`
- lines: 125-186
- chunk: 3/4

```
PyObject *temp_f_trace = frame->f_trace;
        frame->f_trace = NULL;
        if(temp_f_trace != NULL){
            DecRef(temp_f_trace, internalInitializeCustomPyEvalSetTrace->isDebug);
        }
        return -1;
    }
    if (result != internalInitializeCustomPyEvalSetTrace->pyNone) {
        PyObject *tmp = frame->f_trace;
        frame->f_trace = result;
        DecRef(tmp, internalInitializeCustomPyEvalSetTrace->isDebug);
    }
    else {
        DecRef(result, internalInitializeCustomPyEvalSetTrace->isDebug);
    }
    return 0;
}

// Based on ceval.c (PyEval_SetTrace(Py_tracefunc func, PyObject *arg))
template<typename T>
void InternalPySetTrace_Template(T tstate, PyObjectHolder* traceFunc, bool isDebug)
{
    PyObject *temp = tstate->c_traceobj;

    // We can't increase _Py_TracingPossible. Everything else should be equal to CPython.
    // runtime->ceval.tracing_possible += (func != NULL) - (tstate->c_tracefunc != NULL);

    PyObject *arg = traceFunc->ToPython();
    IncRef(arg);
    tstate->c_tracefunc = NULL;
    tstate->c_traceobj = NULL;
    /* Must make sure that profiling is not ignored if 'temp' is freed */
    tstate->use_tracing = tstate->c_profilefunc != NULL;
    if(temp != NULL){
        DecRef(temp, isDebug);
    }
    tstate->c_tracefunc = InternalTraceTrampoline;
    tstate->c_traceobj = arg;
    /* Flag that tracing or profiling is turned on */
    tstate->use_tracing = ((InternalTraceTrampoline != NULL)
                           || (tstate->c_profilefunc != NULL));

};


void InternalPySetTrace(PyThreadState* curThread, PyObjectHolder* traceFunc, bool isDebug, PythonVersion version)
{
    if (PyThreadState_25_27::IsFor(version)) {
        InternalPySetTrace_Template<PyThreadState_25_27*>(reinterpret_cast<PyThreadState_25_27*>(curThread), traceFunc, isDebug);
    } else if (PyThreadState_30_33::IsFor(version)) {
        InternalPySetTrace_Template<PyThreadState_30_33*>(reinterpret_cast<PyThreadState_30_33*>(curThread), traceFunc, isDebug);
    } else if (PyThreadState_34_36::IsFor(version)) {
        InternalPySetTrace_Template<PyThreadState_34_36*>(reinterpret_cast<PyThreadState_34_36*>(curThread), traceFunc, isDebug);
    } else if (PyThreadState_37_38::IsFor(version)) {
        InternalPySetTrace_Template<PyThreadState_37_38*>(reinterpret_cast<PyThreadState_37_38*>(curThread), traceFunc, isDebug);
    } else if (PyThreadState_39::IsFor(version)) {
        InternalPySetTrace_Template<PyThreadState_39*>(reinterpret_cast<PyThreadState_39*>(curThread), traceFunc, isDebug);
    } else if (PyThreadState_310::IsFor(version)) {
        // 3.10 has other changes on the actual algorithm (use_tracing is per-frame now), so, we have a full new version for it.
        InternalPySetTrace_Template310<PyThreadState_310*>(reinterpret_cast<PyThreadState_310*>(curThread), traceFunc, isDebug);
    } else if (PyThreadState_311::IsFor(version)) {
```
