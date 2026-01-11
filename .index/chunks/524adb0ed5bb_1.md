# Chunk: 524adb0ed5bb_1

- source: `.venv-lab/Lib/site-packages/pip/_vendor/packaging/_elffile.py`
- lines: 95-110
- chunk: 2/2

```
 def interpreter(self) -> str | None:
        """
        The path recorded in the ``PT_INTERP`` section header.
        """
        for index in range(self._e_phnum):
            self._f.seek(self._e_phoff + self._e_phentsize * index)
            try:
                data = self._read(self._p_fmt)
            except struct.error:
                continue
            if data[self._p_idx[0]] != 3:  # Not PT_INTERP.
                continue
            self._f.seek(data[self._p_idx[1]])
            return os.fsdecode(self._f.read(data[self._p_idx[2]])).strip("\0")
        return None
```
