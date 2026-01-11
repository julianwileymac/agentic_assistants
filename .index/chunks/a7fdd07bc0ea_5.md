# Chunk: a7fdd07bc0ea_5

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/windows/attach.cpp`
- lines: 315-366
- chunk: 6/11

```
d::flush;
            getPythonThread = getPythonThread13;
        }

        if (curPythonThread == nullptr && getPythonThread == nullptr) {
            // we're missing some APIs, we cannot attach.
            std::cerr << "Error, missing Python threading API!!" << std::endl << std::flush;
            return -240;
        }

        // Either _Py_CheckInterval or _PyEval_[GS]etSwitchInterval are useful, but not required
        DEFINE_PROC_NO_CHECK(intervalCheck, int*, "_Py_CheckInterval", -250);  // optional
        DEFINE_PROC_NO_CHECK(getSwitchInterval, _PyEval_GetSwitchInterval*, "_PyEval_GetSwitchInterval", -260);  // optional
        DEFINE_PROC_NO_CHECK(setSwitchInterval, _PyEval_SetSwitchInterval*, "_PyEval_SetSwitchInterval", -270);  // optional

        auto head = interpHead();
        if (head == nullptr) {
            // this interpreter is loaded but not initialized.
            std::cerr << "Interpreter not initialized! " << std::endl << std::flush;
            return 4;
        }

        // check that we're a supported version
        if (version == PythonVersion_Unknown) {
            std::cerr << "Python version unknown! " << std::endl << std::flush;
            return 5;
        } else if (version == PythonVersion_25 || version == PythonVersion_26 ||
                   version == PythonVersion_30 || version == PythonVersion_31 || version == PythonVersion_32) {
            std::cerr << "Python version unsupported! " << std::endl << std::flush;
            return 5;
        }


        // We always try to initialize threading and import the threading module in the main thread in the code
        // below...
        //
        // We need to initialize multiple threading support but we need to do so safely, so we call
        // Py_AddPendingCall and have our callback then initialize multi threading.  This is completely safe on 2.7
        // and up. Unfortunately that doesn't work if we're not actively running code on the main thread (blocked on a lock
        // or reading input).
        //
        // Another option is to make sure no code is running - if there is no active thread then we can safely call
        // PyEval_InitThreads and we're in business.  But to know this is safe we need to first suspend all the other
        // threads in the process and then inspect if any code is running (note that this is still not ideal because
        // this thread will be the thread head for Python, but still better than not attach at all).
        //
        // Finally if code is running after we've suspended the threads then we can go ahead and do Py_AddPendingCall
        // on down-level interpreters as long as we're sure no one else is making a call to Py_AddPendingCall at the same
        // time.
        //
        // Therefore our strategy becomes: Make the Py_AddPendingCall on interpreters and wait for it. If it doesn't
```
