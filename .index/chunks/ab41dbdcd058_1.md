# Chunk: ab41dbdcd058_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/force_pydevd.py`
- lines: 69-82
- chunk: 2/2

```
ults
pydevd_defaults.PydevdCustomization.DEFAULT_PROTOCOL = pydevd_constants.HTTP_JSON_PROTOCOL

# Enable some defaults related to debugpy such as sending a single notification when
# threads pause and stopping on any exception.
pydevd_defaults.PydevdCustomization.DEBUG_MODE = 'debugpy-dap'

# This is important when pydevd attaches automatically to a subprocess. In this case, we have to
# make sure that debugpy is properly put back in the game for users to be able to use it.
pydevd_defaults.PydevdCustomization.PREIMPORT = '%s;%s' % (
    os.path.dirname(os.path.dirname(debugpy.__file__)), 
    'debugpy._vendored.force_pydevd'
)
```
