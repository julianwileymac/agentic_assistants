# Chunk: eb4bf5d6ad95_5

- source: `.venv-lab/Lib/site-packages/jedi/inference/compiled/subprocess/__init__.py`
- lines: 360-425
- chunk: 6/8

```
ge of a single inference_state shouldn't be that high.
        self._inference_state_deletion_queue.append(inference_state_id)


class Listener:
    """
    Main loop for the subprocess which actually does the inference.

    This class runs within the target environment. It listens to instructions
    from the parent process, runs inference and returns the results.

    The subprocess has a long lifetime and is expected to process several
    requests, including for different `InferenceState` instances in the parent.
    See `CompiledSubprocess` for the parent half of the system.

    Communication is via pickled data sent serially over stdin and stdout.
    Stderr is read only if the child process crashes.

    The request protocol is a 4-tuple of:
     * inference_state_id | None: an opaque identifier of the parent's
       `InferenceState`. An `InferenceState` operating over an
       `InterpreterEnvironment` is created within this process for each of
       these, ensuring that each parent context has a corresponding context
       here. This allows context to be persisted between requests. Unless
       `None`, the local `InferenceState` will be passed to the given function
       as the first positional argument.
     * function | None: the function to run. This is expected to be a member of
       `.functions`. `None` indicates that the corresponding inference state is
       no longer needed and should be dropped.
     * args: positional arguments to the `function`. If any of these are
       `AccessHandle` instances they will be adapted to the local
       `InferenceState` before being passed.
     * kwargs: keyword arguments to the `function`. If any of these are
       `AccessHandle` instances they will be adapted to the local
       `InferenceState` before being passed.

    The result protocol is a 3-tuple of either:
     * (False, None, function result): if the function returns without error, or
     * (True, traceback, exception): if the function raises an exception
    """

    def __init__(self):
        self._inference_states = {}

    def _get_inference_state(self, function, inference_state_id):
        from jedi.inference import InferenceState

        try:
            inference_state = self._inference_states[inference_state_id]
        except KeyError:
            from jedi import InterpreterEnvironment
            inference_state = InferenceState(
                # The project is not actually needed. Nothing should need to
                # access it.
                project=None,
                environment=InterpreterEnvironment()
            )
            self._inference_states[inference_state_id] = inference_state
        return inference_state

    def _run(self, inference_state_id, function, args, kwargs):
        if inference_state_id is None:
            return function(*args, **kwargs)
        elif function is None:
            # Warning: if changing the semantics of context deletion see the comment
```
