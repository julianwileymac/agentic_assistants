# Chunk: 0ce0dbb6c85d_8

- source: `.venv-lab/Lib/site-packages/jedi/inference/names.py`
- lines: 625-678
- chunk: 9/9

```
__init__(self, wrapped_name):
        self._wrapped_name = wrapped_name

    def __getattr__(self, name):
        return getattr(self._wrapped_name, name)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self._wrapped_name)


class StubNameMixin:
    def py__doc__(self):
        from jedi.inference.gradual.conversion import convert_names
        # Stubs are not complicated and we can just follow simple statements
        # that have an equals in them, because they typically make something
        # else public. See e.g. stubs for `requests`.
        names = [self]
        if self.api_type == 'statement' and '=' in self.tree_name.get_definition().children:
            names = [v.name for v in self.infer()]

        names = convert_names(names, prefer_stub_to_compiled=False)
        if self in names:
            return super().py__doc__()
        else:
            # We have signatures ourselves in stubs, so don't use signatures
            # from the implementation.
            return _merge_name_docs(names)


# From here on down we make looking up the sys.version_info fast.
class StubName(StubNameMixin, TreeNameDefinition):
    def infer(self):
        inferred = super().infer()
        if self.string_name == 'version_info' and self.get_root_context().py__name__() == 'sys':
            from jedi.inference.gradual.stub_value import VersionInfo
            return ValueSet(VersionInfo(c) for c in inferred)
        return inferred


class ModuleName(ValueNameMixin, AbstractNameDefinition):
    start_pos = 1, 0

    def __init__(self, value, name):
        self._value = value
        self._name = name

    @property
    def string_name(self):
        return self._name


class StubModuleName(StubNameMixin, ModuleName):
    pass
```
