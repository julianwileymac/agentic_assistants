# Chunk: db6cddaa5f29_2

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevconsole.py`
- lines: 164-237
- chunk: 3/8

```
       return

    activate_mpl_if_already_imported(interpreter)
    from _pydev_bundle.pydev_import_hook import import_hook_manager

    for mod in list(interpreter.mpl_modules_for_patching):
        import_hook_manager.add_module_name(mod, interpreter.mpl_modules_for_patching.pop(mod))


if sys.platform != "win32":
    if not hasattr(os, "kill"):  # Jython may not have it.

        def pid_exists(pid):
            return True

    else:

        def pid_exists(pid):
            # Note that this function in the face of errors will conservatively consider that
            # the pid is still running (because we'll exit the current process when it's
            # no longer running, so, we need to be 100% sure it actually exited).

            import errno

            if pid == 0:
                # According to "man 2 kill" PID 0 has a special meaning:
                # it refers to <<every process in the process group of the
                # calling process>> so we don't want to go any further.
                # If we get here it means this UNIX platform *does* have
                # a process with id 0.
                return True
            try:
                os.kill(pid, 0)
            except OSError as err:
                if err.errno == errno.ESRCH:
                    # ESRCH == No such process
                    return False
                elif err.errno == errno.EPERM:
                    # EPERM clearly means there's a process to deny access to
                    return True
                else:
                    # According to "man 2 kill" possible error values are
                    # (EINVAL, EPERM, ESRCH) therefore we should never get
                    # here. If we do, although it's an error, consider it
                    # exists (see first comment in this function).
                    return True
            else:
                return True

else:

    def pid_exists(pid):
        # Note that this function in the face of errors will conservatively consider that
        # the pid is still running (because we'll exit the current process when it's
        # no longer running, so, we need to be 100% sure it actually exited).
        import ctypes

        kernel32 = ctypes.windll.kernel32

        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        ERROR_INVALID_PARAMETER = 0x57
        STILL_ACTIVE = 259

        process = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_QUERY_LIMITED_INFORMATION, 0, pid)
        if not process:
            err = kernel32.GetLastError()
            if err == ERROR_INVALID_PARAMETER:
                # Means it doesn't exist (pid parameter is wrong).
                return False

            # There was some unexpected error (such as access denied), so
            # consider it exists (although it could be something else, but we don't want
```
