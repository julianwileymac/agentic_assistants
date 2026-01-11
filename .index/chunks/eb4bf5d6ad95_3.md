# Chunk: eb4bf5d6ad95_3

- source: `.venv-lab/Lib/site-packages/jedi/inference/compiled/subprocess/__init__.py`
- lines: 216-302
- chunk: 4/8

```
    return AccessPath(self._convert_access_handles(obj.accesses))
        return obj

    def __del__(self):
        if self._used and not self._compiled_subprocess.is_crashed:
            self._compiled_subprocess.delete_inference_state(self._inference_state_id)


class CompiledSubprocess:
    """
    A subprocess which runs inference within a target environment.

    This class manages the interface to a single instance of such a process as
    well as the lifecycle of the process itself. See `.__main__` and `Listener`
    for the implementation of the subprocess and details of the protocol.

    A single live instance of this is maintained by `jedi.api.environment.Environment`,
    so that typically a single subprocess is used at a time.
    """

    is_crashed = False

    def __init__(self, executable, env_vars=None):
        self._executable = executable
        self._env_vars = env_vars
        self._inference_state_deletion_queue = collections.deque()
        self._cleanup_callable = lambda: None

    def __repr__(self):
        pid = os.getpid()
        return '<%s _executable=%r, is_crashed=%r, pid=%r>' % (
            self.__class__.__name__,
            self._executable,
            self.is_crashed,
            pid,
        )

    @memoize_method
    def _get_process(self):
        debug.dbg('Start environment subprocess %s', self._executable)
        parso_path = sys.modules['parso'].__file__
        args = (
            self._executable,
            _MAIN_PATH,
            os.path.dirname(os.path.dirname(parso_path)),
            '.'.join(str(x) for x in sys.version_info[:3]),
        )
        process = _GeneralizedPopen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self._env_vars
        )
        self._stderr_queue = queue.Queue()
        self._stderr_thread = t = Thread(
            target=_enqueue_output,
            args=(process.stderr, self._stderr_queue)
        )
        t.daemon = True
        t.start()
        # Ensure the subprocess is properly cleaned up when the object
        # is garbage collected.
        self._cleanup_callable = weakref.finalize(self,
                                                  _cleanup_process,
                                                  process,
                                                  t)
        return process

    def run(self, inference_state_id, function, args=(), kwargs={}):
        # Delete old inference_states.
        while True:
            try:
                delete_id = self._inference_state_deletion_queue.pop()
            except IndexError:
                break
            else:
                self._send(delete_id, None)

        assert callable(function)
        return self._send(inference_state_id, function, args, kwargs)

    def get_sys_path(self):
        return self._send(None, functions.get_sys_path, (), {})

    def _kill(self):
```
