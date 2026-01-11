# Chunk: 7a17ebd0fa6e_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydev_bundle/_pydev_saved_modules.py`
- lines: 72-135
- chunk: 2/2

```
e__])
                break

        if msg:
            raise DebuggerInitializationError(msg)


with VerifyShadowedImport("threading") as verify_shadowed:
    import threading

    verify_shadowed.check(threading, ["Thread", "settrace", "setprofile", "Lock", "RLock", "current_thread"])
    ThreadingEvent = threading.Event
    ThreadingLock = threading.Lock
    threading_current_thread = threading.current_thread

with VerifyShadowedImport("time") as verify_shadowed:
    import time

    verify_shadowed.check(time, ["sleep", "time", "mktime"])

with VerifyShadowedImport("socket") as verify_shadowed:
    import socket

    verify_shadowed.check(socket, ["socket", "gethostname", "getaddrinfo"])

with VerifyShadowedImport("select") as verify_shadowed:
    import select

    verify_shadowed.check(select, ["select"])

with VerifyShadowedImport("code") as verify_shadowed:
    import code as _code

    verify_shadowed.check(_code, ["compile_command", "InteractiveInterpreter"])

with VerifyShadowedImport("_thread") as verify_shadowed:
    import _thread as thread

    verify_shadowed.check(thread, ["start_new_thread", "start_new", "allocate_lock"])

with VerifyShadowedImport("queue") as verify_shadowed:
    import queue as _queue

    verify_shadowed.check(_queue, ["Queue", "LifoQueue", "Empty", "Full", "deque"])

with VerifyShadowedImport("xmlrpclib") as verify_shadowed:
    import xmlrpc.client as xmlrpclib

    verify_shadowed.check(xmlrpclib, ["ServerProxy", "Marshaller", "Server"])

with VerifyShadowedImport("xmlrpc.server") as verify_shadowed:
    import xmlrpc.server as xmlrpcserver

    verify_shadowed.check(xmlrpcserver, ["SimpleXMLRPCServer"])

with VerifyShadowedImport("http.server") as verify_shadowed:
    import http.server as BaseHTTPServer

    verify_shadowed.check(BaseHTTPServer, ["BaseHTTPRequestHandler"])

# If set, this is a version of the threading.enumerate that doesn't have the patching to remove the pydevd threads.
# Note: as it can't be set during execution, don't import the name (import the module and access it through its name).
pydevd_saved_threading_enumerate = None
```
