# Chunk: befe5c6ecdcf_2

- source: `.venv-lab/Lib/site-packages/pip/_internal/req/req_install.py`
- lines: 136-208
- chunk: 3/12

```
isting
        # distribution before installing this requirement.
        self.should_reinstall = False
        # Temporary build location
        self._temp_build_dir: TempDirectory | None = None
        # Set to True after successful installation
        self.install_succeeded: bool | None = None
        # Supplied options
        self.hash_options = hash_options if hash_options else {}
        self.config_settings = config_settings
        # Set to True after successful preparation of this requirement
        self.prepared = False
        # User supplied requirement are explicitly requested for installation
        # by the user via CLI arguments or requirements files, as opposed to,
        # e.g. dependencies, extras or constraints.
        self.user_supplied = user_supplied

        self.isolated = isolated
        self.build_env: BuildEnvironment = NoOpBuildEnvironment()

        # For PEP 517, the directory where we request the project metadata
        # gets stored. We need this to pass to build_wheel, so the backend
        # can ensure that the wheel matches the metadata (see the PEP for
        # details).
        self.metadata_directory: str | None = None

        # The cached metadata distribution that this requirement represents.
        # See get_dist / set_dist.
        self._distribution: BaseDistribution | None = None

        # The static build requirements (from pyproject.toml)
        self.pyproject_requires: list[str] | None = None

        # Build requirements that we will check are available
        self.requirements_to_check: list[str] = []

        # The PEP 517 backend we should use to build the project
        self.pep517_backend: BuildBackendHookCaller | None = None

        # This requirement needs more preparation before it can be built
        self.needs_more_preparation = False

        # This requirement needs to be unpacked before it can be installed.
        self._archive_source: Path | None = None

    def __str__(self) -> str:
        if self.req:
            s = redact_auth_from_requirement(self.req)
            if self.link:
                s += f" from {redact_auth_from_url(self.link.url)}"
        elif self.link:
            s = redact_auth_from_url(self.link.url)
        else:
            s = "<InstallRequirement>"
        if self.satisfied_by is not None:
            if self.satisfied_by.location is not None:
                location = display_path(self.satisfied_by.location)
            else:
                location = "<memory>"
            s += f" in {location}"
        if self.comes_from:
            if isinstance(self.comes_from, str):
                comes_from: str | None = self.comes_from
            else:
                comes_from = self.comes_from.from_path()
            if comes_from:
                s += f" (from {comes_from})"
        return s

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} object: "
```
