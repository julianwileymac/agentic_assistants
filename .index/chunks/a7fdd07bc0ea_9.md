# Chunk: a7fdd07bc0ea_9

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/windows/attach.cpp`
- lines: 514-595
- chunk: 10/11

```
::cerr << "Unable to initialize threads in the given timeout! " << std::endl << std::flush;
            return 8;
        }

        GilHolder gilLock(gilEnsure, gilRelease);   // acquire and hold the GIL until done...

        pyRun_SimpleString(command);
        return 0;

    }




    // ======================================== Code related to setting tracing to existing threads.


    /**
     * This function is meant to be called to execute some arbitrary python code to be
     * run. It'll initialize threads as needed and then run the code with pyRun_SimpleString.
     *
     * @param command: the python code to be run
     * @param attachInfo: pointer to an int specifying whether we should show debug info (1) or not (0).
     **/
    DECLDIR int AttachAndRunPythonCode(const char *command, int *attachInfo )
    {

        int SHOW_DEBUG_INFO = 1;

        bool showDebugInfo = (*attachInfo & SHOW_DEBUG_INFO) != 0;

        if (showDebugInfo) {
            std::cout << "AttachAndRunPythonCode started (showing debug info). " << std::endl << std::flush;
        }

        ModuleInfo moduleInfo = GetPythonModule();
        if (moduleInfo.errorGettingModule != 0) {
            return moduleInfo.errorGettingModule;
        }
        HMODULE module = moduleInfo.module;
        int attached = DoAttach(module, moduleInfo.isDebug, command, showDebugInfo);

        if (attached != 0) {
            std::cerr << "Error when injecting code in target process. Error code (on windows): " << attached << std::endl << std::flush;
        }
        return attached;
    }


    DECLDIR int PrintDebugInfo() {
        PRINT("Getting debug info...");
        ModuleInfo moduleInfo = GetPythonModule();
        if (moduleInfo.errorGettingModule != 0) {
            PRINT("Error getting python module");
            return 0;
        }
        HMODULE module = moduleInfo.module;

        DEFINE_PROC(interpHead, PyInterpreterState_Head*, "PyInterpreterState_Head", 0);
        DEFINE_PROC(threadHead, PyInterpreterState_ThreadHead*, "PyInterpreterState_ThreadHead", 0);
        DEFINE_PROC(threadNext, PyThreadState_Next*, "PyThreadState_Next", 160);
        DEFINE_PROC(gilEnsure, PyGILState_Ensure*, "PyGILState_Ensure", 0);
        DEFINE_PROC(gilRelease, PyGILState_Release*, "PyGILState_Release", 0);

        auto head = interpHead();
        if (head == nullptr) {
            // this interpreter is loaded but not initialized.
            PRINT("Interpreter not initialized!");
            return 0;
        }

        auto version = GetPythonVersion(module);
        printf("Python version: %d\n", version);

        GilHolder gilLock(gilEnsure, gilRelease);   // acquire and hold the GIL until done...
        auto curThread = threadHead(head);
        if (curThread == nullptr) {
            PRINT("Thread head is NULL.")
            return 0;
        }

```
