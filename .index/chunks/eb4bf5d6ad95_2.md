# Chunk: eb4bf5d6ad95_2

- source: `.venv-lab/Lib/site-packages/jedi/inference/compiled/subprocess/__init__.py`
- lines: 161-226
- chunk: 3/8

```
que id we'll pass to the subprocess to identify the context (an
        # `InferenceState`) which should be used for the request. This allows us
        # to make subsequent requests which operate on results from previous
        # ones, while keeping a single subprocess which can work with several
        # contexts in the parent process. Once it is no longer needed(i.e: when
        # this class goes away), we also use this id to indicate that the
        # subprocess can discard the context.
        #
        # Note: this id is deliberately coupled to this class (and not to
        # `InferenceState`) as this class manages access handle mappings which
        # must correspond to those in the subprocess. This approach also avoids
        # race conditions from successive `InferenceState`s with the same object
        # id (as observed while adding support for Python 3.13).
        #
        # This value does not need to be the `id()` of this instance, we merely
        # need to ensure that it enables the (visible) lifetime of the context
        # within the subprocess to match that of this class. We therefore also
        # depend on the semantics of `CompiledSubprocess.delete_inference_state`
        # for correctness.
        self._inference_state_id = id(self)

    def __getattr__(self, name):
        func = _get_function(name)

        def wrapper(*args, **kwargs):
            self._used = True

            result = self._compiled_subprocess.run(
                self._inference_state_id,
                func,
                args=args,
                kwargs=kwargs,
            )
            # IMO it should be possible to create a hook in pickle.load to
            # mess with the loaded objects. However it's extremely complicated
            # to work around this so just do it with this call. ~ dave
            return self._convert_access_handles(result)

        return wrapper

    def _convert_access_handles(self, obj):
        if isinstance(obj, SignatureParam):
            return SignatureParam(*self._convert_access_handles(tuple(obj)))
        elif isinstance(obj, tuple):
            return tuple(self._convert_access_handles(o) for o in obj)
        elif isinstance(obj, list):
            return [self._convert_access_handles(o) for o in obj]
        elif isinstance(obj, AccessHandle):
            try:
                # Rewrite the access handle to one we're already having.
                obj = self.get_access_handle(obj.id)
            except KeyError:
                obj.add_subprocess(self)
                self.set_access_handle(obj)
        elif isinstance(obj, AccessPath):
            return AccessPath(self._convert_access_handles(obj.accesses))
        return obj

    def __del__(self):
        if self._used and not self._compiled_subprocess.is_crashed:
            self._compiled_subprocess.delete_inference_state(self._inference_state_id)


class CompiledSubprocess:
    """
```
