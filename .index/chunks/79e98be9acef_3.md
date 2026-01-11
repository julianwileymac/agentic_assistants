# Chunk: 79e98be9acef_3

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/common/py_custom_pyeval_settrace.hpp`
- lines: 183-193
- chunk: 4/4

```
10 has other changes on the actual algorithm (use_tracing is per-frame now), so, we have a full new version for it.
        InternalPySetTrace_Template310<PyThreadState_310*>(reinterpret_cast<PyThreadState_310*>(curThread), traceFunc, isDebug);
    } else if (PyThreadState_311::IsFor(version)) {
        InternalPySetTrace_Template311<PyThreadState_311*>(reinterpret_cast<PyThreadState_311*>(curThread), traceFunc, isDebug);
    } else {
        printf("Unable to set trace to target thread with Python version: %d", version);
    }
}


#endif //_PY_CUSTOM_PYEVAL_SETTRACE_HPP_
```
