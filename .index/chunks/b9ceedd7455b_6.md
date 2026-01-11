# Chunk: b9ceedd7455b_6

- source: `.venv-lab/Lib/site-packages/anyio/_core/_fileio.py`
- lines: 517-611
- chunk: 7/10

```
cel=True)

    async def hardlink_to(
        self, target: str | bytes | PathLike[str] | PathLike[bytes]
    ) -> None:
        if isinstance(target, Path):
            target = target._path

        await to_thread.run_sync(os.link, target, self)

    @classmethod
    async def home(cls) -> Path:
        home_path = await to_thread.run_sync(pathlib.Path.home)
        return cls(home_path)

    def is_absolute(self) -> bool:
        return self._path.is_absolute()

    async def is_block_device(self) -> bool:
        return await to_thread.run_sync(
            self._path.is_block_device, abandon_on_cancel=True
        )

    async def is_char_device(self) -> bool:
        return await to_thread.run_sync(
            self._path.is_char_device, abandon_on_cancel=True
        )

    async def is_dir(self) -> bool:
        return await to_thread.run_sync(self._path.is_dir, abandon_on_cancel=True)

    async def is_fifo(self) -> bool:
        return await to_thread.run_sync(self._path.is_fifo, abandon_on_cancel=True)

    async def is_file(self) -> bool:
        return await to_thread.run_sync(self._path.is_file, abandon_on_cancel=True)

    if sys.version_info >= (3, 12):

        async def is_junction(self) -> bool:
            return await to_thread.run_sync(self._path.is_junction)

    async def is_mount(self) -> bool:
        return await to_thread.run_sync(
            os.path.ismount, self._path, abandon_on_cancel=True
        )

    def is_reserved(self) -> bool:
        return self._path.is_reserved()

    async def is_socket(self) -> bool:
        return await to_thread.run_sync(self._path.is_socket, abandon_on_cancel=True)

    async def is_symlink(self) -> bool:
        return await to_thread.run_sync(self._path.is_symlink, abandon_on_cancel=True)

    async def iterdir(self) -> AsyncIterator[Path]:
        gen = (
            self._path.iterdir()
            if sys.version_info < (3, 13)
            else await to_thread.run_sync(self._path.iterdir, abandon_on_cancel=True)
        )
        async for path in _PathIterator(gen):
            yield path

    def joinpath(self, *args: str | PathLike[str]) -> Path:
        return Path(self._path.joinpath(*args))

    async def lchmod(self, mode: int) -> None:
        await to_thread.run_sync(self._path.lchmod, mode)

    async def lstat(self) -> os.stat_result:
        return await to_thread.run_sync(self._path.lstat, abandon_on_cancel=True)

    async def mkdir(
        self, mode: int = 0o777, parents: bool = False, exist_ok: bool = False
    ) -> None:
        await to_thread.run_sync(self._path.mkdir, mode, parents, exist_ok)

    @overload
    async def open(
        self,
        mode: OpenBinaryMode,
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
```
