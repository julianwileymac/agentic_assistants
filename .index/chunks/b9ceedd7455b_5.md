# Chunk: b9ceedd7455b_5

- source: `.venv-lab/Lib/site-packages/anyio/_core/_fileio.py`
- lines: 448-529
- chunk: 6/10

```
       # Upstream does not handle anyio.Path properly as a PathLike
            target = pathlib.Path(target)
            return Path(await to_thread.run_sync(self._path.move, target))

        async def move_into(
            self,
            target_dir: str | os.PathLike[str],
        ) -> Path:
            return Path(await to_thread.run_sync(self._path.move_into, target_dir))

    def is_relative_to(self, other: str | PathLike[str]) -> bool:
        try:
            self.relative_to(other)
            return True
        except ValueError:
            return False

    async def chmod(self, mode: int, *, follow_symlinks: bool = True) -> None:
        func = partial(os.chmod, follow_symlinks=follow_symlinks)
        return await to_thread.run_sync(func, self._path, mode)

    @classmethod
    async def cwd(cls) -> Path:
        path = await to_thread.run_sync(pathlib.Path.cwd)
        return cls(path)

    async def exists(self) -> bool:
        return await to_thread.run_sync(self._path.exists, abandon_on_cancel=True)

    async def expanduser(self) -> Path:
        return Path(
            await to_thread.run_sync(self._path.expanduser, abandon_on_cancel=True)
        )

    if sys.version_info < (3, 12):
        # Python 3.11 and earlier
        def glob(self, pattern: str) -> AsyncIterator[Path]:
            gen = self._path.glob(pattern)
            return _PathIterator(gen)
    elif (3, 12) <= sys.version_info < (3, 13):
        # changed in Python 3.12:
        # - The case_sensitive parameter was added.
        def glob(
            self,
            pattern: str,
            *,
            case_sensitive: bool | None = None,
        ) -> AsyncIterator[Path]:
            gen = self._path.glob(pattern, case_sensitive=case_sensitive)
            return _PathIterator(gen)
    elif sys.version_info >= (3, 13):
        # Changed in Python 3.13:
        # - The recurse_symlinks parameter was added.
        # - The pattern parameter accepts a path-like object.
        def glob(  # type: ignore[misc] # mypy doesn't allow for differing signatures in a conditional block
            self,
            pattern: str | PathLike[str],
            *,
            case_sensitive: bool | None = None,
            recurse_symlinks: bool = False,
        ) -> AsyncIterator[Path]:
            gen = self._path.glob(
                pattern,  # type: ignore[arg-type]
                case_sensitive=case_sensitive,
                recurse_symlinks=recurse_symlinks,
            )
            return _PathIterator(gen)

    async def group(self) -> str:
        return await to_thread.run_sync(self._path.group, abandon_on_cancel=True)

    async def hardlink_to(
        self, target: str | bytes | PathLike[str] | PathLike[bytes]
    ) -> None:
        if isinstance(target, Path):
            target = target._path

        await to_thread.run_sync(os.link, target, self)

    @classmethod
    async def home(cls) -> Path:
```
