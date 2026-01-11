# Chunk: a7fdd07bc0ea_10

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/windows/attach.cpp`
- lines: 586-641
- chunk: 11/11

```
 printf("Python version: %d\n", version);

        GilHolder gilLock(gilEnsure, gilRelease);   // acquire and hold the GIL until done...
        auto curThread = threadHead(head);
        if (curThread == nullptr) {
            PRINT("Thread head is NULL.")
            return 0;
        }

        for (auto curThread = threadHead(head); curThread != nullptr; curThread = threadNext(curThread)) {
            printf("Found thread id: %d\n", GetPythonThreadId(version, curThread));
        }

        PRINT("Finished getting debug info.")
        return 0;
    }


    /**
     * This function may be called to set a tracing function to existing python threads.
     **/
    DECLDIR int AttachDebuggerTracing(bool showDebugInfo, void* pSetTraceFunc, void* pTraceFunc, unsigned int threadId, void* pPyNone)
    {
        ModuleInfo moduleInfo = GetPythonModule();
        if (moduleInfo.errorGettingModule != 0) {
            return moduleInfo.errorGettingModule;
        }
        HMODULE module = moduleInfo.module;
        if (showDebugInfo) {
            std::cout << "Setting sys trace for existing threads." << std::endl << std::flush;
        }
        int attached = 0;
        PyObjectHolder traceFunc(moduleInfo.isDebug, reinterpret_cast<PyObject*>(pTraceFunc), true);
        PyObjectHolder setTraceFunc(moduleInfo.isDebug, reinterpret_cast<PyObject*>(pSetTraceFunc), true);
        PyObjectHolder pyNone(moduleInfo.isDebug, reinterpret_cast<PyObject*>(pPyNone), true);

        int temp = InternalSetSysTraceFunc(module, moduleInfo.isDebug, showDebugInfo, &traceFunc, &setTraceFunc, threadId, &pyNone);
        if (temp == 0) {
            // we've successfully attached the debugger
            return 0;
        } else {
           if (temp > attached) {
               //I.e.: the higher the value the more significant it is.
               attached = temp;
            }
        }

        if (showDebugInfo) {
            std::cout << "Setting sys trace for existing threads failed with code: " << attached << "." << std::endl << std::flush;
        }
        return attached;
    }

}

```
