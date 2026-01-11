# Chunk: eb4bf5d6ad95_7

- source: `.venv-lab/Lib/site-packages/jedi/inference/compiled/subprocess/__init__.py`
- lines: 497-513
- chunk: 8/8

```
ame, file=sys.stderr)
        return partial(self._workaround, name)

    def _workaround(self, name, *args, **kwargs):
        """
        TODO Currently we're passing slice objects around. This should not
        happen. They are also the only unhashable objects that we're passing
        around.
        """
        if args and isinstance(args[0], slice):
            return self._subprocess.get_compiled_method_return(self.id, name, *args, **kwargs)
        return self._cached_results(name, *args, **kwargs)

    @memoize_method
    def _cached_results(self, name, *args, **kwargs):
        return self._subprocess.get_compiled_method_return(self.id, name, *args, **kwargs)
```
