# Chunk: db6cddaa5f29_4

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevconsole.py`
- lines: 304-389
- chunk: 5/8

```
)


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
        exitfunc = None

    if IPYTHON:
        from _pydev_bundle.pydev_ipython_console import InterpreterInterface

        if exitfunc is not None:
            sys.exitfunc = exitfunc
        else:
            try:
                delattr(sys, "exitfunc")
            except:
                pass
except:
    IPYTHON = False
    pass


# =======================================================================================================================
# _DoExit
# =======================================================================================================================
def do_exit(*args):
    """
    We have to override the exit because calling sys.exit will only actually exit the main thread,
    and as we're in a Xml-rpc server, that won't work.
    """

    try:
        import java.lang.System

        java.lang.System.exit(1)
    except ImportError:
        if len(args) == 1:
            os._exit(args[0])
        else:
            os._exit(0)


# =======================================================================================================================
# start_console_server
# =======================================================================================================================
def start_console_server(host, port, interpreter):
    try:
        if port == 0:
            host = ""

        # I.e.: supporting the internal Jython version in PyDev to create a Jython interactive console inside Eclipse.
        from _pydev_bundle.pydev_imports import SimpleXMLRPCServer as XMLRPCServer  # @Reimport

        try:
            server = XMLRPCServer((host, port), logRequests=False, allow_none=True)

        except:
            sys.stderr.write(
                'Error starting server with host: "%s", port: "%s", client_port: "%s"\n' % (host, port, interpreter.client_port)
            )
            sys.stderr.flush()
            raise

        # Tell UMD the proper default namespace
        _set_globals_function(interpreter.get_namespace)

        server.register_function(interpreter.execLine)
        server.register_function(interpreter.execMultipleLines)
        server.register_function(interpreter.getCompletions)
        server.register_function(interpreter.getFrame)
        server.register_function(interpreter.getVariable)
        server.register_function(interpreter.changeVariable)
        server.register_function(interpreter.getDescription)
        server.register_function(interpreter.close)
        server.register_function(interpreter.interrupt)
        server.register_function(interpreter.handshake)
```
