# Chunk: b9ceedd7455b_7

- source: `.venv-lab/Lib/site-packages/anyio/_core/_fileio.py`
- lines: 599-687
- chunk: 8/10

```
ode: OpenBinaryMode,
        buffering: int = ...,
        encoding: str | None = ...,
        errors: str | None = ...,
        newline: str | None = ...,
    ) -> AsyncFile[bytes]: ...

    @overload
    async def open(
        self,
        mode: OpenTextMode = ...,
        buffering: int = ...,
        encoding: str | None = ...,
        errors: str | None = ...,
        newline: str | None = ...,
    ) -> AsyncFile[str]: ...

    async def open(
        self,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> AsyncFile[Any]:
        fp = await to_thread.run_sync(
            self._path.open, mode, buffering, encoding, errors, newline
        )
        return AsyncFile(fp)

    async def owner(self) -> str:
        return await to_thread.run_sync(self._path.owner, abandon_on_cancel=True)

    async def read_bytes(self) -> bytes:
        return await to_thread.run_sync(self._path.read_bytes)

    async def read_text(
        self, encoding: str | None = None, errors: str | None = None
    ) -> str:
        return await to_thread.run_sync(self._path.read_text, encoding, errors)

    if sys.version_info >= (3, 12):

        def relative_to(
            self, *other: str | PathLike[str], walk_up: bool = False
        ) -> Path:
            # relative_to() should work with any PathLike but it doesn't
            others = [pathlib.Path(other) for other in other]
            return Path(self._path.relative_to(*others, walk_up=walk_up))

    else:

        def relative_to(self, *other: str | PathLike[str]) -> Path:
            return Path(self._path.relative_to(*other))

    async def readlink(self) -> Path:
        target = await to_thread.run_sync(os.readlink, self._path)
        return Path(target)

    async def rename(self, target: str | pathlib.PurePath | Path) -> Path:
        if isinstance(target, Path):
            target = target._path

        await to_thread.run_sync(self._path.rename, target)
        return Path(target)

    async def replace(self, target: str | pathlib.PurePath | Path) -> Path:
        if isinstance(target, Path):
            target = target._path

        await to_thread.run_sync(self._path.replace, target)
        return Path(target)

    async def resolve(self, strict: bool = False) -> Path:
        func = partial(self._path.resolve, strict=strict)
        return Path(await to_thread.run_sync(func, abandon_on_cancel=True))

    if sys.version_info < (3, 12):
        # Pre Python 3.12
        def rglob(self, pattern: str) -> AsyncIterator[Path]:
            gen = self._path.rglob(pattern)
            return _PathIterator(gen)
    elif (3, 12) <= sys.version_info < (3, 13):
        # Changed in Python 3.12:
        # - The case_sensitive parameter was added.
        def rglob(
            self, pattern: str, *, case_sensitive: bool | None = None
        ) -> AsyncIterator[Path]:
```
