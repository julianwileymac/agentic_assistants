# Chunk: dacf7e9b9f9b_3

- source: `.venv-lab/Lib/site-packages/setuptools/_distutils/command/install_lib.py`
- lines: 224-239
- chunk: 4/4

```
lled as they are named in the build tree.
        The files in this list correspond one-to-one to the output
        filenames returned by 'get_outputs()'.
        """
        inputs = []

        if self.distribution.has_pure_modules():
            build_py = self.get_finalized_command('build_py')
            inputs.extend(build_py.get_outputs())

        if self.distribution.has_ext_modules():
            build_ext = self.get_finalized_command('build_ext')
            inputs.extend(build_ext.get_outputs())

        return inputs
```
