# Chunk: eb4bf5d6ad95_6

- source: `.venv-lab/Lib/site-packages/jedi/inference/compiled/subprocess/__init__.py`
- lines: 417-505
- chunk: 7/8

```
ate
        return inference_state

    def _run(self, inference_state_id, function, args, kwargs):
        if inference_state_id is None:
            return function(*args, **kwargs)
        elif function is None:
            # Warning: if changing the semantics of context deletion see the comment
            # in `InferenceStateSubprocess.__init__` regarding potential race
            # conditions.
            del self._inference_states[inference_state_id]
        else:
            inference_state = self._get_inference_state(function, inference_state_id)

            # Exchange all handles
            args = list(args)
            for i, arg in enumerate(args):
                if isinstance(arg, AccessHandle):
                    args[i] = inference_state.compiled_subprocess.get_access_handle(arg.id)
            for key, value in kwargs.items():
                if isinstance(value, AccessHandle):
                    kwargs[key] = inference_state.compiled_subprocess.get_access_handle(value.id)

            return function(inference_state, *args, **kwargs)

    def listen(self):
        stdout = sys.stdout
        # Mute stdout. Nobody should actually be able to write to it,
        # because stdout is used for IPC.
        sys.stdout = open(os.devnull, 'w')
        stdin = sys.stdin
        stdout = stdout.buffer
        stdin = stdin.buffer

        while True:
            try:
                payload = pickle_load(stdin)
            except EOFError:
                # It looks like the parent process closed.
                # Don't make a big fuss here and just exit.
                exit(0)
            try:
                result = False, None, self._run(*payload)
            except Exception as e:
                result = True, traceback.format_exc(), e

            pickle_dump(result, stdout, PICKLE_PROTOCOL)


class AccessHandle:
    def __init__(
        self,
        subprocess: _InferenceStateProcess,
        access: DirectObjectAccess,
        id_: int,
    ) -> None:
        self.access = access
        self._subprocess = subprocess
        self.id = id_

    def add_subprocess(self, subprocess):
        self._subprocess = subprocess

    def __repr__(self):
        try:
            detail = self.access
        except AttributeError:
            detail = '#' + str(self.id)
        return '<%s of %s>' % (self.__class__.__name__, detail)

    def __getstate__(self):
        return self.id

    def __setstate__(self, state):
        self.id = state

    def __getattr__(self, name):
        if name in ('id', 'access') or name.startswith('_'):
            raise AttributeError("Something went wrong with unpickling")

        # print('getattr', name, file=sys.stderr)
        return partial(self._workaround, name)

    def _workaround(self, name, *args, **kwargs):
        """
        TODO Currently we're passing slice objects around. This should not
        happen. They are also the only unhashable objects that we're passing
        around.
```
