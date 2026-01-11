# Chunk: eb4bf5d6ad95_4

- source: `.venv-lab/Lib/site-packages/jedi/inference/compiled/subprocess/__init__.py`
- lines: 291-369
- chunk: 5/8

```
            break
            else:
                self._send(delete_id, None)

        assert callable(function)
        return self._send(inference_state_id, function, args, kwargs)

    def get_sys_path(self):
        return self._send(None, functions.get_sys_path, (), {})

    def _kill(self):
        self.is_crashed = True
        self._cleanup_callable()

    def _send(self, inference_state_id, function, args=(), kwargs={}):
        if self.is_crashed:
            raise InternalError("The subprocess %s has crashed." % self._executable)

        data = inference_state_id, function, args, kwargs
        try:
            pickle_dump(data, self._get_process().stdin, PICKLE_PROTOCOL)
        except BrokenPipeError:
            self._kill()
            raise InternalError("The subprocess %s was killed. Maybe out of memory?"
                                % self._executable)

        try:
            is_exception, traceback, result = pickle_load(self._get_process().stdout)
        except EOFError as eof_error:
            try:
                stderr = self._get_process().stderr.read().decode('utf-8', 'replace')
            except Exception as exc:
                stderr = '<empty/not available (%r)>' % exc
            self._kill()
            _add_stderr_to_debug(self._stderr_queue)
            raise InternalError(
                "The subprocess %s has crashed (%r, stderr=%s)." % (
                    self._executable,
                    eof_error,
                    stderr,
                ))

        _add_stderr_to_debug(self._stderr_queue)

        if is_exception:
            # Replace the attribute error message with a the traceback. It's
            # way more informative.
            result.args = (traceback,)
            raise result
        return result

    def delete_inference_state(self, inference_state_id):
        """
        Indicate that an inference state (in the subprocess) is no longer
        needed.

        The state corresponding to the given id will become inaccessible and the
        id may safely be re-used to refer to a different context.

        Note: it is not guaranteed that the corresponding state will actually be
        deleted immediately.
        """
        # Warning: if changing the semantics of context deletion see the comment
        # in `InferenceStateSubprocess.__init__` regarding potential race
        # conditions.

        # Currently we are not deleting the related state instantly. They only
        # get deleted once the subprocess is used again. It would probably a
        # better solution to move all of this into a thread. However, the memory
        # usage of a single inference_state shouldn't be that high.
        self._inference_state_deletion_queue.append(inference_state_id)


class Listener:
    """
    Main loop for the subprocess which actually does the inference.

    This class runs within the target environment. It listens to instructions
```
