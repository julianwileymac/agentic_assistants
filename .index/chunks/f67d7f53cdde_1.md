# Chunk: f67d7f53cdde_1

- source: `.venv-lab/Lib/site-packages/setuptools/command/install_lib.py`
- lines: 85-138
- chunk: 2/2

```
tation'):
            return

        base = os.path.join('__pycache__', '__init__.' + sys.implementation.cache_tag)
        yield base + '.pyc'
        yield base + '.pyo'
        yield base + '.opt-1.pyc'
        yield base + '.opt-2.pyc'

    def copy_tree(
        self,
        infile: StrPath,
        outfile: str,
        # override: Using actual booleans
        preserve_mode: bool = True,  # type: ignore[override]
        preserve_times: bool = True,  # type: ignore[override]
        preserve_symlinks: bool = False,  # type: ignore[override]
        level: object = 1,
    ) -> list[str]:
        assert preserve_mode
        assert preserve_times
        assert not preserve_symlinks
        exclude = self.get_exclusions()

        if not exclude:
            return orig.install_lib.copy_tree(self, infile, outfile)

        # Exclude namespace package __init__.py* files from the output

        from setuptools.archive_util import unpack_directory

        from distutils import log

        outfiles: list[str] = []

        def pf(src: str, dst: str):
            if dst in exclude:
                log.warn("Skipping installation of %s (namespace package)", dst)
                return False

            log.info("copying %s -> %s", src, os.path.dirname(dst))
            outfiles.append(dst)
            return dst

        unpack_directory(infile, outfile, pf)
        return outfiles

    def get_outputs(self):
        outputs = orig.install_lib.get_outputs(self)
        exclude = self.get_exclusions()
        if exclude:
            return [f for f in outputs if f not in exclude]
        return outputs
```
