# Chunk: 41e4d2ba0eec_2

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_dont_trace_files.py`
- lines: 146-179
- chunk: 3/3

```
.py': PYDEV_FILE,
    'pydevd_runpy.py': PYDEV_FILE,
    'pydevd_safe_repr.py': PYDEV_FILE,
    'pydevd_save_locals.py': PYDEV_FILE,
    'pydevd_schema.py': PYDEV_FILE,
    'pydevd_schema_log.py': PYDEV_FILE,
    'pydevd_signature.py': PYDEV_FILE,
    'pydevd_source_mapping.py': PYDEV_FILE,
    'pydevd_stackless.py': PYDEV_FILE,
    'pydevd_suspended_frames.py': PYDEV_FILE,
    'pydevd_sys_monitoring.py': PYDEV_FILE,
    'pydevd_thread_lifecycle.py': PYDEV_FILE,
    'pydevd_thread_wrappers.py': PYDEV_FILE,
    'pydevd_timeout.py': PYDEV_FILE,
    'pydevd_trace_dispatch.py': PYDEV_FILE,
    'pydevd_trace_dispatch_regular.py': PYDEV_FILE,
    'pydevd_traceproperty.py': PYDEV_FILE,
    'pydevd_tracing.py': PYDEV_FILE,
    'pydevd_utils.py': PYDEV_FILE,
    'pydevd_vars.py': PYDEV_FILE,
    'pydevd_vm_type.py': PYDEV_FILE,
    'pydevd_xml.py': PYDEV_FILE,
}

# if we try to trace io.py it seems it can get halted (see http://bugs.python.org/issue4716)
DONT_TRACE['io.py'] = LIB_FILE

# Don't trace common encodings too
DONT_TRACE['cp1252.py'] = LIB_FILE
DONT_TRACE['utf_8.py'] = LIB_FILE
DONT_TRACE['codecs.py'] = LIB_FILE

# fmt: on
```
