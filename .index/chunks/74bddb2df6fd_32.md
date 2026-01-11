# Chunk: 74bddb2df6fd_32

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 2259-2270
- chunk: 33/33

```
 = debug.system
                    for pid in debug.get_debugee_pids():
                        try:
                            system.get_process(pid).debug_break()
                            success = True
                        except:
                            traceback.print_exc()
                except:
                    traceback.print_exc()
                if not success:
                    raise  # This should never happen!
```
