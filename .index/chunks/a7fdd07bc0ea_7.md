# Chunk: a7fdd07bc0ea_7

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/windows/attach.cpp`
- lines: 406-461
- chunk: 8/11

```
ialized! " << std::endl << std::flush;
            }

        } else {
            int saveIntervalCheck;
            unsigned long saveLongIntervalCheck;
            if (intervalCheck != nullptr) {
                // not available on 3.2
                saveIntervalCheck = *intervalCheck;
                *intervalCheck = -1;    // lower the interval check so pending calls are processed faster
                saveLongIntervalCheck = 0; // prevent compiler warning
            } else if (getSwitchInterval != nullptr && setSwitchInterval != nullptr) {
                saveLongIntervalCheck = getSwitchInterval();
                setSwitchInterval(0);
                saveIntervalCheck = 0; // prevent compiler warning
            }
            else {
                saveIntervalCheck = 0; // prevent compiler warning
                saveLongIntervalCheck = 0; // prevent compiler warning
            }

            // If threads weren't initialized in our pending call, instead of giving a timeout, try
            // to initialize it in this thread.
            for(int attempts = 0; !threadsInited() && attempts < 20; attempts++) {
                if(attempts > 0){
                    // If we haven't been able to do it in the first time, wait a bit before retrying.
                    Sleep(10);
                }

                ThreadMap suspendedThreads;
                if (showDebugInfo) {
                    std::cout << "SuspendThreads(suspendedThreads, addPendingCall, threadsInited);" << std::endl << std::flush;
                }
                SuspendThreads(suspendedThreads, addPendingCall, threadsInited);

                if(!threadsInited()){ // Check again with threads suspended.
                    if (showDebugInfo) {
                        std::cout << "ENTERED if (!threadsInited()) {" << std::endl << std::flush;
                    }
                    auto curPyThread = getPythonThread ? getPythonThread() : *curPythonThread;

                    if (curPyThread == nullptr) {
                        if (showDebugInfo) {
                            std::cout << "ENTERED if (curPyThread == nullptr) {" << std::endl << std::flush;
                        }
                         // no threads are currently running, it is safe to initialize multi threading.
                         PyGILState_STATE gilState;
                         if (version >= PythonVersion_34) {
                             // in 3.4 due to http://bugs.python.org/issue20891,
                             // we need to create our thread state manually
                             // before we can call PyGILState_Ensure() before we
                             // can call PyEval_InitThreads().

                             // Don't require this function unless we need it.
                             auto threadNew = (PyThreadState_NewFunc*)GetProcAddress(module, "PyThreadState_New");
```
