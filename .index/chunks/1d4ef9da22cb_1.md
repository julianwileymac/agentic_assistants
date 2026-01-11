# Chunk: 1d4ef9da22cb_1

- source: `.venv-lab/Lib/site-packages/setuptools/command/dist_info.py`
- lines: 84-104
- chunk: 2/2

```
       try:
                yield
            finally:
                _rm(dir_path, ignore_errors=True)
                shutil.move(bkp_name, dir_path)
        else:
            yield

    def run(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.egg_info.run()
        egg_info_dir = self.egg_info.egg_info
        assert os.path.isdir(egg_info_dir), ".egg-info dir should have been created"

        log.info(f"creating '{os.path.abspath(self.dist_info_dir)}'")
        bdist_wheel = self.get_finalized_command('bdist_wheel')

        # TODO: if bdist_wheel if merged into setuptools, just add "keep_egg_info" there
        with self._maybe_bkp_dir(egg_info_dir, self.keep_egg_info):
            bdist_wheel.egg2dist(egg_info_dir, self.dist_info_dir)
```
