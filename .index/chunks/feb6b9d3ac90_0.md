# Chunk: feb6b9d3ac90_0

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_scripts.py`
- lines: 1-13
- chunk: 1/1

```
from setuptools import _scripts


class TestWindowsScriptWriter:
    def test_header(self):
        hdr = _scripts.WindowsScriptWriter.get_header('')
        assert hdr.startswith('#!')
        assert hdr.endswith('\n')
        hdr = hdr.lstrip('#!')
        hdr = hdr.rstrip('\n')
        # header should not start with an escaped quote
        assert not hdr.startswith('\\"')
```
