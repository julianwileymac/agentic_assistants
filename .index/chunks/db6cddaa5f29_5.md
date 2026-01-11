# Chunk: db6cddaa5f29_5

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevconsole.py`
- lines: 383-465
- chunk: 6/8

```
riable)
        server.register_function(interpreter.changeVariable)
        server.register_function(interpreter.getDescription)
        server.register_function(interpreter.close)
        server.register_function(interpreter.interrupt)
        server.register_function(interpreter.handshake)
        server.register_function(interpreter.connectToDebugger)
        server.register_function(interpreter.hello)
        server.register_function(interpreter.getArray)
        server.register_function(interpreter.evaluate)
        server.register_function(interpreter.ShowConsole)
        server.register_function(interpreter.loadFullValue)

        # Functions for GUI main loop integration
        server.register_function(interpreter.enableGui)

        if port == 0:
            (h, port) = server.socket.getsockname()

            print(port)
            print(interpreter.client_port)

        while True:
            try:
                server.serve_forever()
            except:
                # Ugly code to be py2/3 compatible
                # https://sw-brainwy.rhcloud.com/tracker/PyDev/534:
                # Unhandled "interrupted system call" error in the pydevconsol.py
                e = sys.exc_info()[1]
                retry = False
                try:
                    retry = e.args[0] == 4  # errno.EINTR
                except:
                    pass
                if not retry:
                    raise
                    # Otherwise, keep on going
        return server
    except:
        pydev_log.exception()
        # Notify about error to avoid long waiting
        connection_queue = interpreter.get_connect_status_queue()
        if connection_queue is not None:
            connection_queue.put(False)


def start_server(host, port, client_port):
    # replace exit (see comments on method)
    # note that this does not work in jython!!! (sys method can't be replaced).
    sys.exit = do_exit

    interpreter = InterpreterInterface(host, client_port, threading.current_thread())

    start_new_thread(start_console_server, (host, port, interpreter))

    process_exec_queue(interpreter)


def get_ipython_hidden_vars():
    if IPYTHON and hasattr(__builtin__, "interpreter"):
        interpreter = get_interpreter()
        return interpreter.get_ipython_hidden_vars_dict()


def get_interpreter():
    try:
        interpreterInterface = getattr(__builtin__, "interpreter")
    except AttributeError:
        interpreterInterface = InterpreterInterface(None, None, threading.current_thread())
        __builtin__.interpreter = interpreterInterface
        sys.stderr.write(interpreterInterface.get_greeting_msg())
        sys.stderr.flush()

    return interpreterInterface


def get_completions(text, token, globals, locals):
    interpreterInterface = get_interpreter()

    interpreterInterface.interpreter.update(globals, locals)

```
