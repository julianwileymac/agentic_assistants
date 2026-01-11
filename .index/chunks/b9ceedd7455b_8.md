# Chunk: b9ceedd7455b_8

- source: `.venv-lab/Lib/site-packages/anyio/_core/_fileio.py`
- lines: 679-757
- chunk: 9/10

```
ern)
            return _PathIterator(gen)
    elif (3, 12) <= sys.version_info < (3, 13):
        # Changed in Python 3.12:
        # - The case_sensitive parameter was added.
        def rglob(
            self, pattern: str, *, case_sensitive: bool | None = None
        ) -> AsyncIterator[Path]:
            gen = self._path.rglob(pattern, case_sensitive=case_sensitive)
            return _PathIterator(gen)
    elif sys.version_info >= (3, 13):
        # Changed in Python 3.13:
        # - The recurse_symlinks parameter was added.
        # - The pattern parameter accepts a path-like object.
        def rglob(  # type: ignore[misc] # mypy doesn't allow for differing signatures in a conditional block
            self,
            pattern: str | PathLike[str],
            *,
            case_sensitive: bool | None = None,
            recurse_symlinks: bool = False,
        ) -> AsyncIterator[Path]:
            gen = self._path.rglob(
                pattern,  # type: ignore[arg-type]
                case_sensitive=case_sensitive,
                recurse_symlinks=recurse_symlinks,
            )
            return _PathIterator(gen)

    async def rmdir(self) -> None:
        await to_thread.run_sync(self._path.rmdir)

    async def samefile(self, other_path: str | PathLike[str]) -> bool:
        if isinstance(other_path, Path):
            other_path = other_path._path

        return await to_thread.run_sync(
            self._path.samefile, other_path, abandon_on_cancel=True
        )

    async def stat(self, *, follow_symlinks: bool = True) -> os.stat_result:
        func = partial(os.stat, follow_symlinks=follow_symlinks)
        return await to_thread.run_sync(func, self._path, abandon_on_cancel=True)

    async def symlink_to(
        self,
        target: str | bytes | PathLike[str] | PathLike[bytes],
        target_is_directory: bool = False,
    ) -> None:
        if isinstance(target, Path):
            target = target._path

        await to_thread.run_sync(self._path.symlink_to, target, target_is_directory)

    async def touch(self, mode: int = 0o666, exist_ok: bool = True) -> None:
        await to_thread.run_sync(self._path.touch, mode, exist_ok)

    async def unlink(self, missing_ok: bool = False) -> None:
        try:
            await to_thread.run_sync(self._path.unlink)
        except FileNotFoundError:
            if not missing_ok:
                raise

    if sys.version_info >= (3, 12):

        async def walk(
            self,
            top_down: bool = True,
            on_error: Callable[[OSError], object] | None = None,
            follow_symlinks: bool = False,
        ) -> AsyncIterator[tuple[Path, list[str], list[str]]]:
            def get_next_value() -> tuple[pathlib.Path, list[str], list[str]] | None:
                try:
                    return next(gen)
                except StopIteration:
                    return None

            gen = self._path.walk(top_down, on_error, follow_symlinks)
```
