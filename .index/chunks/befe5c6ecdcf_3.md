# Chunk: befe5c6ecdcf_3

- source: `.venv-lab/Lib/site-packages/pip/_internal/req/req_install.py`
- lines: 198-286
- chunk: 4/12

```
_from: str | None = self.comes_from
            else:
                comes_from = self.comes_from.from_path()
            if comes_from:
                s += f" (from {comes_from})"
        return s

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} object: "
            f"{str(self)} editable={self.editable!r}>"
        )

    def format_debug(self) -> str:
        """An un-tested helper for getting state, for debugging."""
        attributes = vars(self)
        names = sorted(attributes)

        state = (f"{attr}={attributes[attr]!r}" for attr in sorted(names))
        return "<{name} object: {{{state}}}>".format(
            name=self.__class__.__name__,
            state=", ".join(state),
        )

    # Things that are valid for all kinds of requirements?
    @property
    def name(self) -> str | None:
        if self.req is None:
            return None
        return self.req.name

    @functools.cached_property
    def supports_pyproject_editable(self) -> bool:
        assert self.pep517_backend
        with self.build_env:
            runner = runner_with_spinner_message(
                "Checking if build backend supports build_editable"
            )
            with self.pep517_backend.subprocess_runner(runner):
                return "build_editable" in self.pep517_backend._supported_features()

    @property
    def specifier(self) -> SpecifierSet:
        assert self.req is not None
        return self.req.specifier

    @property
    def is_direct(self) -> bool:
        """Whether this requirement was specified as a direct URL."""
        return self.original_link is not None

    @property
    def is_pinned(self) -> bool:
        """Return whether I am pinned to an exact version.

        For example, some-package==1.2 is pinned; some-package>1.2 is not.
        """
        assert self.req is not None
        specifiers = self.req.specifier
        return len(specifiers) == 1 and next(iter(specifiers)).operator in {"==", "==="}

    def match_markers(self, extras_requested: Iterable[str] | None = None) -> bool:
        if not extras_requested:
            # Provide an extra to safely evaluate the markers
            # without matching any extra
            extras_requested = ("",)
        if self.markers is not None:
            return any(
                self.markers.evaluate({"extra": extra}) for extra in extras_requested
            )
        else:
            return True

    @property
    def has_hash_options(self) -> bool:
        """Return whether any known-good hashes are specified as options.

        These activate --require-hashes mode; hashes specified as part of a
        URL do not.

        """
        return bool(self.hash_options)

    def hashes(self, trust_internet: bool = True) -> Hashes:
        """Return a hash-comparer that considers my option- and URL-based
        hashes to be known-good.

        Hashes in URLs--ones embedded in the requirements file, not ones
```
