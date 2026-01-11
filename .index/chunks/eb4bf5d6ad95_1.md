# Chunk: eb4bf5d6ad95_1

- source: `.venv-lab/Lib/site-packages/jedi/inference/compiled/subprocess/__init__.py`
- lines: 79-165
- chunk: 2/8

```
err_queue.get_nowait()
            line = line.decode('utf-8', 'replace')
            debug.warning('stderr output: %s' % line.rstrip('\n'))
        except queue.Empty:
            break


def _get_function(name):
    return getattr(functions, name)


def _cleanup_process(process, thread):
    try:
        process.kill()
        process.wait()
    except OSError:
        # Raised if the process is already killed.
        pass
    thread.join()
    for stream in [process.stdin, process.stdout, process.stderr]:
        try:
            stream.close()
        except OSError:
            # Raised if the stream is broken.
            pass


class _InferenceStateProcess:
    def __init__(self, inference_state: 'InferenceState') -> None:
        self._inference_state_weakref = weakref.ref(inference_state)
        self._handles: Dict[int, AccessHandle] = {}

    def get_or_create_access_handle(self, obj):
        id_ = id(obj)
        try:
            return self.get_access_handle(id_)
        except KeyError:
            access = DirectObjectAccess(self._inference_state_weakref(), obj)
            handle = AccessHandle(self, access, id_)
            self.set_access_handle(handle)
            return handle

    def get_access_handle(self, id_):
        return self._handles[id_]

    def set_access_handle(self, handle):
        self._handles[handle.id] = handle


class InferenceStateSameProcess(_InferenceStateProcess):
    """
    Basically just an easy access to functions.py. It has the same API
    as InferenceStateSubprocess and does the same thing without using a subprocess.
    This is necessary for the Interpreter process.
    """
    def __getattr__(self, name):
        return partial(_get_function(name), self._inference_state_weakref())


class InferenceStateSubprocess(_InferenceStateProcess):
    """
    API to functionality which will run in a subprocess.

    This mediates the interaction between an `InferenceState` and the actual
    execution of functionality running within a `CompiledSubprocess`. Available
    functions are defined in `.functions`, though should be accessed via
    attributes on this class of the same name.

    This class is responsible for indicating that the `InferenceState` within
    the subprocess can be removed once the corresponding instance in the parent
    goes away.
    """

    def __init__(
        self,
        inference_state: 'InferenceState',
        compiled_subprocess: 'CompiledSubprocess',
    ) -> None:
        super().__init__(inference_state)
        self._used = False
        self._compiled_subprocess = compiled_subprocess

        # Opaque id we'll pass to the subprocess to identify the context (an
        # `InferenceState`) which should be used for the request. This allows us
        # to make subsequent requests which operate on results from previous
        # ones, while keeping a single subprocess which can work with several
```
