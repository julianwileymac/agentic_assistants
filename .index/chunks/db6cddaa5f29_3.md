# Chunk: db6cddaa5f29_3

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevconsole.py`
- lines: 231-318
- chunk: 4/8

```
f err == ERROR_INVALID_PARAMETER:
                # Means it doesn't exist (pid parameter is wrong).
                return False

            # There was some unexpected error (such as access denied), so
            # consider it exists (although it could be something else, but we don't want
            # to raise any errors -- so, just consider it exists).
            return True

        try:
            zero = ctypes.c_int(0)
            exit_code = ctypes.pointer(zero)

            exit_code_suceeded = kernel32.GetExitCodeProcess(process, exit_code)
            if not exit_code_suceeded:
                # There was some unexpected error (such as access denied), so
                # consider it exists (although it could be something else, but we don't want
                # to raise any errors -- so, just consider it exists).
                return True

            elif bool(exit_code.contents.value) and int(exit_code.contents.value) != STILL_ACTIVE:
                return False
        finally:
            kernel32.CloseHandle(process)

        return True


def process_exec_queue(interpreter):
    init_mpl_in_console(interpreter)
    from pydev_ipython.inputhook import get_inputhook

    try:
        kill_if_pid_not_alive = int(os.environ.get("PYDEV_ECLIPSE_PID", "-1"))
    except:
        kill_if_pid_not_alive = -1

    while 1:
        if kill_if_pid_not_alive != -1:
            if not pid_exists(kill_if_pid_not_alive):
                exit()

        # Running the request may have changed the inputhook in use
        inputhook = get_inputhook()

        if _ProcessExecQueueHelper._debug_hook:
            _ProcessExecQueueHelper._debug_hook()

        if inputhook:
            try:
                # Note: it'll block here until return_control returns True.
                inputhook()
            except:
                pydev_log.exception()
        try:
            try:
                code_fragment = interpreter.exec_queue.get(block=True, timeout=1 / 20.0)  # 20 calls/second
            except _queue.Empty:
                continue

            if callable(code_fragment):
                # It can be a callable (i.e.: something that must run in the main
                # thread can be put in the queue for later execution).
                code_fragment()
            else:
                more = interpreter.add_exec(code_fragment)
        except KeyboardInterrupt:
            interpreter.buffer = None
            continue
        except SystemExit:
            raise
        except:
            pydev_log.exception("Error processing queue on pydevconsole.")
            exit()


if "IPYTHONENABLE" in os.environ:
    IPYTHON = os.environ["IPYTHONENABLE"] == "True"
else:
    # By default, don't use IPython because occasionally changes
    # in IPython break pydevd.
    IPYTHON = False

try:
    try:
        exitfunc = sys.exitfunc
    except AttributeError:
```
