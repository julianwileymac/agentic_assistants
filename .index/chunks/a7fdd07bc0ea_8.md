# Chunk: a7fdd07bc0ea_8

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/windows/attach.cpp`
- lines: 456-528
- chunk: 9/11

```
n call PyGILState_Ensure() before we
                             // can call PyEval_InitThreads().

                             // Don't require this function unless we need it.
                             auto threadNew = (PyThreadState_NewFunc*)GetProcAddress(module, "PyThreadState_New");
                             if (threadNew != nullptr) {
                                 threadNew(head);
                             }
                         }

                         if (version >= PythonVersion_32) {
                             // in 3.2 due to the new GIL and later we can't call Py_InitThreads
                             // without a thread being initialized.
                             // So we use PyGilState_Ensure here to first
                             // initialize the current thread, and then we use
                             // Py_InitThreads to bring up multi-threading.
                             // Some context here: http://bugs.python.org/issue11329
                             // http://pytools.codeplex.com/workitem/834
                            gilState = gilEnsure();
                        }
                        else {
                            gilState = PyGILState_LOCKED; // prevent compiler warning
                         }

                        if (showDebugInfo) {
                            std::cout << "Called initThreads()" << std::endl << std::flush;
                        }
                        // Initialize threads in our secondary thread (this is NOT ideal because
                        // this thread will be the thread head), but is still better than not being
                        // able to attach if the main thread is not actually running any code.
                        initThreads();

                         if (version >= PythonVersion_32) {
                             // we will release the GIL here
                            gilRelease(gilState);
                         } else {
                             releaseLock();
                         }
                    }
                }
                ResumeThreads(suspendedThreads);
            }


            if (intervalCheck != nullptr) {
                *intervalCheck = saveIntervalCheck;
            } else if (setSwitchInterval != nullptr) {
                setSwitchInterval(saveLongIntervalCheck);
            }

        }

        if (g_heap != nullptr) {
            HeapDestroy(g_heap);
            g_heap = nullptr;
        }

        if (!threadsInited()) {
            std::cerr << "Unable to initialize threads in the given timeout! " << std::endl << std::flush;
            return 8;
        }

        GilHolder gilLock(gilEnsure, gilRelease);   // acquire and hold the GIL until done...

        pyRun_SimpleString(command);
        return 0;

    }




```
