# Chunk: a7fdd07bc0ea_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/windows/attach.cpp`
- lines: 71-135
- chunk: 2/11

```
lock
typedef PyObject* (Py_CompileString)(const char *str, const char *filename, int start);
typedef PyObject* (PyEval_EvalCode)(PyObject *co, PyObject *globals, PyObject *locals);
typedef PyObject* (PyDict_GetItemString)(PyObject *p, const char *key);
typedef PyObject* (PyEval_GetBuiltins)();
typedef int (PyDict_SetItemString)(PyObject *dp, const char *key, PyObject *item);
typedef int (PyEval_ThreadsInitialized)();
typedef int (Py_AddPendingCall)(int (*func)(void *), void*);
typedef PyObject* (PyString_FromString)(const char* s);
typedef void PyEval_SetTrace(Py_tracefunc func, PyObject *obj);
typedef PyObject* (PyErr_Print)();
typedef PyObject* (PyObject_SetAttrString)(PyObject *o, const char *attr_name, PyObject* value);
typedef PyObject* (PyBool_FromLong)(long v);
typedef unsigned long (_PyEval_GetSwitchInterval)(void);
typedef void (_PyEval_SetSwitchInterval)(unsigned long microseconds);
typedef PyGILState_STATE PyGILState_EnsureFunc(void);
typedef void PyGILState_ReleaseFunc(PyGILState_STATE);
typedef PyThreadState *PyThreadState_NewFunc(PyInterpreterState *interp);

typedef PyObject *PyList_New(Py_ssize_t len);
typedef int PyList_Append(PyObject *list, PyObject *item);



std::wstring GetCurrentModuleFilename() {
    HMODULE hModule = nullptr;
    if (GetModuleHandleEx(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT, (LPCTSTR)GetCurrentModuleFilename, &hModule) != 0) {
        wchar_t filename[MAX_PATH];
        GetModuleFileName(hModule, filename, MAX_PATH);
        return filename;
    }
    return std::wstring();
}


struct InitializeThreadingInfo {
    PyImport_ImportModule* pyImportMod;
    PyEval_Lock* initThreads;

    CRITICAL_SECTION cs;
    HANDLE initedEvent;  // Note: only access with mutex locked (and check if not already nullptr).
    bool completed; // Note: only access with mutex locked
};


int AttachCallback(void *voidInitializeThreadingInfo) {
    // initialize us for threading, this will acquire the GIL if not already created, and is a nop if the GIL is created.
    // This leaves us in the proper state when we return back to the runtime whether the GIL was created or not before
    // we were called.
    InitializeThreadingInfo* initializeThreadingInfo = reinterpret_cast<InitializeThreadingInfo*>(voidInitializeThreadingInfo);
    initializeThreadingInfo->initThreads(); // Note: calling multiple times is ok.
    initializeThreadingInfo->pyImportMod("threading");

    EnterCriticalSection(&initializeThreadingInfo->cs);
    initializeThreadingInfo->completed = true;
    if(initializeThreadingInfo->initedEvent != nullptr) {
        SetEvent(initializeThreadingInfo->initedEvent);
    }
    LeaveCriticalSection(&initializeThreadingInfo->cs);
    return 0;
}


// create a custom heap for our unordered map.  This is necessary because if we suspend a thread while in a heap function
```
