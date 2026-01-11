# Chunk: a7fdd07bc0ea_4

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/windows/attach.cpp`
- lines: 261-322
- chunk: 5/11

```

}



extern "C"
{

    /**
     * The returned value signals the error that happened!
     *
     * Return codes:
     * 0 = all OK.
     * 1 = Py_IsInitialized not found
     * 2 = Py_IsInitialized returned false
     * 3 = Missing Python API
     * 4 = Interpreter not initialized
     * 5 = Python version unknown
     * 6 = Connect timeout
     **/
	int DoAttach(HMODULE module, bool isDebug, const char *command, bool showDebugInfo )
	{
        auto isInit = reinterpret_cast<Py_IsInitialized*>(GetProcAddress(module, "Py_IsInitialized"));

        if (isInit == nullptr) {
            std::cerr << "Py_IsInitialized not found. " << std::endl << std::flush;
            return 1;
        }
        if (!isInit()) {
            std::cerr << "Py_IsInitialized returned false. " << std::endl << std::flush;
            return 2;
        }

        auto version = GetPythonVersion(module);

        // found initialized Python runtime, gather and check the APIs we need for a successful attach...
        DEFINE_PROC(addPendingCall, Py_AddPendingCall*, "Py_AddPendingCall", -100);
        DEFINE_PROC(interpHead, PyInterpreterState_Head*, "PyInterpreterState_Head", -110);
        DEFINE_PROC(gilEnsure, PyGILState_Ensure*, "PyGILState_Ensure", -120);
        DEFINE_PROC(gilRelease, PyGILState_Release*, "PyGILState_Release", -130);
        DEFINE_PROC(threadHead, PyInterpreterState_ThreadHead*, "PyInterpreterState_ThreadHead", -140);
        DEFINE_PROC(initThreads, PyEval_Lock*, "PyEval_InitThreads", -150);
        DEFINE_PROC(releaseLock, PyEval_Lock*, "PyEval_ReleaseLock", -160);
        DEFINE_PROC(threadsInited, PyEval_ThreadsInitialized*, "PyEval_ThreadsInitialized", -170);
        DEFINE_PROC(threadNext, PyThreadState_Next*, "PyThreadState_Next", -180);
        DEFINE_PROC(pyImportMod, PyImport_ImportModule*, "PyImport_ImportModule", -190);
        DEFINE_PROC(pyNone, PyObject*, "_Py_NoneStruct", -2000);
        DEFINE_PROC(pyRun_SimpleString, PyRun_SimpleString*, "PyRun_SimpleString", -210);

        // Either _PyThreadState_Current or _PyThreadState_UncheckedGet are required
        DEFINE_PROC_NO_CHECK(curPythonThread, PyThreadState**, "_PyThreadState_Current", -220);  // optional
        DEFINE_PROC_NO_CHECK(getPythonThread, _PyThreadState_UncheckedGet*, "_PyThreadState_UncheckedGet", -230);  // optional
        DEFINE_PROC_NO_CHECK(getPythonThread13, _PyThreadState_GetCurrent*, "_PyThreadState_GetCurrent", -231);  // optional
        if (getPythonThread == nullptr && getPythonThread13 != nullptr) {
            std::cout << "Using Python 3.13 or later, using _PyThreadState_GetCurrent" << std::endl << std::flush;
            getPythonThread = getPythonThread13;
        }

        if (curPythonThread == nullptr && getPythonThread == nullptr) {
            // we're missing some APIs, we cannot attach.
            std::cerr << "Error, missing Python threading API!!" << std::endl << std::flush;
```
