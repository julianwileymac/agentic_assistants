# Chunk: b9ceedd7455b_4

- source: `.venv-lab/Lib/site-packages/anyio/_core/_fileio.py`
- lines: 359-456
- chunk: 5/10

```
    def parents(self) -> Sequence[Path]:
        return tuple(Path(p) for p in self._path.parents)

    @property
    def parent(self) -> Path:
        return Path(self._path.parent)

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def suffix(self) -> str:
        return self._path.suffix

    @property
    def suffixes(self) -> list[str]:
        return self._path.suffixes

    @property
    def stem(self) -> str:
        return self._path.stem

    async def absolute(self) -> Path:
        path = await to_thread.run_sync(self._path.absolute)
        return Path(path)

    def as_posix(self) -> str:
        return self._path.as_posix()

    def as_uri(self) -> str:
        return self._path.as_uri()

    if sys.version_info >= (3, 13):
        parser: ClassVar[ModuleType] = pathlib.Path.parser

        @classmethod
        def from_uri(cls, uri: str) -> Path:
            return Path(pathlib.Path.from_uri(uri))

        def full_match(
            self, path_pattern: str, *, case_sensitive: bool | None = None
        ) -> bool:
            return self._path.full_match(path_pattern, case_sensitive=case_sensitive)

        def match(
            self, path_pattern: str, *, case_sensitive: bool | None = None
        ) -> bool:
            return self._path.match(path_pattern, case_sensitive=case_sensitive)
    else:

        def match(self, path_pattern: str) -> bool:
            return self._path.match(path_pattern)

    if sys.version_info >= (3, 14):

        @property
        def info(self) -> Any:  # TODO: add return type annotation when Typeshed gets it
            return self._path.info

        async def copy(
            self,
            target: str | os.PathLike[str],
            *,
            follow_symlinks: bool = True,
            preserve_metadata: bool = False,
        ) -> Path:
            func = partial(
                self._path.copy,
                follow_symlinks=follow_symlinks,
                preserve_metadata=preserve_metadata,
            )
            return Path(await to_thread.run_sync(func, pathlib.Path(target)))

        async def copy_into(
            self,
            target_dir: str | os.PathLike[str],
            *,
            follow_symlinks: bool = True,
            preserve_metadata: bool = False,
        ) -> Path:
            func = partial(
                self._path.copy_into,
                follow_symlinks=follow_symlinks,
                preserve_metadata=preserve_metadata,
            )
            return Path(await to_thread.run_sync(func, pathlib.Path(target_dir)))

        async def move(self, target: str | os.PathLike[str]) -> Path:
            # Upstream does not handle anyio.Path properly as a PathLike
            target = pathlib.Path(target)
            return Path(await to_thread.run_sync(self._path.move, target))

        async def move_into(
            self,
            target_dir: str | os.PathLike[str],
        ) -> Path:
```
