# Chunk: b9ceedd7455b_9

- source: `.venv-lab/Lib/site-packages/anyio/_core/_fileio.py`
- lines: 749-798
- chunk: 10/10

```
 list[str]]]:
            def get_next_value() -> tuple[pathlib.Path, list[str], list[str]] | None:
                try:
                    return next(gen)
                except StopIteration:
                    return None

            gen = self._path.walk(top_down, on_error, follow_symlinks)
            while True:
                value = await to_thread.run_sync(get_next_value)
                if value is None:
                    return

                root, dirs, paths = value
                yield Path(root), dirs, paths

    def with_name(self, name: str) -> Path:
        return Path(self._path.with_name(name))

    def with_stem(self, stem: str) -> Path:
        return Path(self._path.with_name(stem + self._path.suffix))

    def with_suffix(self, suffix: str) -> Path:
        return Path(self._path.with_suffix(suffix))

    def with_segments(self, *pathsegments: str | PathLike[str]) -> Path:
        return Path(*pathsegments)

    async def write_bytes(self, data: bytes) -> int:
        return await to_thread.run_sync(self._path.write_bytes, data)

    async def write_text(
        self,
        data: str,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> int:
        # Path.write_text() does not support the "newline" parameter before Python 3.10
        def sync_write_text() -> int:
            with self._path.open(
                "w", encoding=encoding, errors=errors, newline=newline
            ) as fp:
                return fp.write(data)

        return await to_thread.run_sync(sync_write_text)


PathLike.register(Path)
```
