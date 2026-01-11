# Chunk: a7fdd07bc0ea_6

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/windows/attach.cpp`
- lines: 361-415
- chunk: 7/11

```
ad and do Py_AddPendingCall
        // on down-level interpreters as long as we're sure no one else is making a call to Py_AddPendingCall at the same
        // time.
        //
        // Therefore our strategy becomes: Make the Py_AddPendingCall on interpreters and wait for it. If it doesn't
        // call after a timeout, suspend all threads - if a threads is in Py_AddPendingCall resume and try again.  Once we've got all of the threads
        // stopped and not in Py_AddPendingCall (which calls no functions its self, you can see this and it's size in the
        // debugger) then see if we have a current thread. If not go ahead and initialize multiple threading (it's now safe,
        // no Python code is running).

        InitializeThreadingInfo *initializeThreadingInfo = new InitializeThreadingInfo();
        initializeThreadingInfo->pyImportMod = pyImportMod;
        initializeThreadingInfo->initThreads = initThreads;
        initializeThreadingInfo->initedEvent = CreateEvent(nullptr, TRUE, FALSE, nullptr);
        InitializeCriticalSection(&initializeThreadingInfo->cs);

        // Add the call to initialize threading.
        addPendingCall(&AttachCallback, initializeThreadingInfo);

        ::WaitForSingleObject(initializeThreadingInfo->initedEvent, 5000);

        // Whether this completed or not, release the event handle as we won't use it anymore.
        EnterCriticalSection(&initializeThreadingInfo->cs);
        CloseHandle(initializeThreadingInfo->initedEvent);
        bool completed = initializeThreadingInfo->completed;
        initializeThreadingInfo->initedEvent = nullptr;
        LeaveCriticalSection(&initializeThreadingInfo->cs);

        if(completed) {
            // Note that this structure will leak if addPendingCall did not complete in the timeout
            // (we can't release now because it's possible that it'll still be called).
            DeleteCriticalSection(&initializeThreadingInfo->cs);
            delete initializeThreadingInfo;
            if (showDebugInfo) {
                std::cout << "addPendingCall to initialize threads/import threading completed. " << std::endl << std::flush;
            }
        } else {
            if (showDebugInfo) {
                std::cout << "addPendingCall to initialize threads/import threading did NOT complete. " << std::endl << std::flush;
            }
        }

        if (threadsInited()) {
            // Note that since Python 3.7, threads are *always* initialized!
            if (showDebugInfo) {
                std::cout << "Threads initialized! " << std::endl << std::flush;
            }

        } else {
            int saveIntervalCheck;
            unsigned long saveLongIntervalCheck;
            if (intervalCheck != nullptr) {
                // not available on 3.2
                saveIntervalCheck = *intervalCheck;
```
