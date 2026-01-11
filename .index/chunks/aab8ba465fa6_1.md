# Chunk: aab8ba465fa6_1

- source: `.venv-lab/Lib/site-packages/setuptools/_distutils/tests/test_install_lib.py`
- lines: 85-111
- chunk: 2/2

```
spam', '__init__.py')
        self.write_file(f, '# python package')
        cmd.distribution.ext_modules = [Extension('foo', ['xxx'])]
        cmd.distribution.packages = ['spam']
        cmd.distribution.script_name = 'setup.py'

        # get_inputs should return 2 elements: spam/__init__.py and
        # foo.import-tag-abiflags.so / foo.pyd
        inputs = cmd.get_inputs()
        assert len(inputs) == 2, inputs

    def test_dont_write_bytecode(self, caplog):
        # makes sure byte_compile is not used
        dist = self.create_dist()[1]
        cmd = install_lib(dist)
        cmd.compile = True
        cmd.optimize = 1

        old_dont_write_bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        try:
            cmd.byte_compile([])
        finally:
            sys.dont_write_bytecode = old_dont_write_bytecode

        assert 'byte-compiling is disabled' in caplog.messages[0]
```
