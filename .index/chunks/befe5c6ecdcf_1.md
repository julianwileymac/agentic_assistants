# Chunk: befe5c6ecdcf_1

- source: `.venv-lab/Lib/site-packages/pip/_internal/req/req_install.py`
- lines: 75-143
- chunk: 2/12

```
 Marker | None = None,
        isolated: bool = False,
        *,
        hash_options: dict[str, list[str]] | None = None,
        config_settings: dict[str, str | list[str]] | None = None,
        constraint: bool = False,
        extras: Collection[str] = (),
        user_supplied: bool = False,
        permit_editable_wheels: bool = False,
    ) -> None:
        assert req is None or isinstance(req, Requirement), req
        self.req = req
        self.comes_from = comes_from
        self.constraint = constraint
        self.editable = editable
        self.permit_editable_wheels = permit_editable_wheels

        # source_dir is the local directory where the linked requirement is
        # located, or unpacked. In case unpacking is needed, creating and
        # populating source_dir is done by the RequirementPreparer. Note this
        # is not necessarily the directory where pyproject.toml or setup.py is
        # located - that one is obtained via unpacked_source_directory.
        self.source_dir: str | None = None
        if self.editable:
            assert link
            if link.is_file:
                self.source_dir = os.path.normpath(os.path.abspath(link.file_path))

        # original_link is the direct URL that was provided by the user for the
        # requirement, either directly or via a constraints file.
        if link is None and req and req.url:
            # PEP 508 URL requirement
            link = Link(req.url)
        self.link = self.original_link = link

        # When this InstallRequirement is a wheel obtained from the cache of locally
        # built wheels, this is the source link corresponding to the cache entry, which
        # was used to download and build the cached wheel.
        self.cached_wheel_source_link: Link | None = None

        # Information about the location of the artifact that was downloaded . This
        # property is guaranteed to be set in resolver results.
        self.download_info: DirectUrl | None = None

        # Path to any downloaded or already-existing package.
        self.local_file_path: str | None = None
        if self.link and self.link.is_file:
            self.local_file_path = self.link.file_path

        if extras:
            self.extras = extras
        elif req:
            self.extras = req.extras
        else:
            self.extras = set()
        if markers is None and req:
            markers = req.marker
        self.markers = markers

        # This holds the Distribution object if this requirement is already installed.
        self.satisfied_by: BaseDistribution | None = None
        # Whether the installation process should try to uninstall an existing
        # distribution before installing this requirement.
        self.should_reinstall = False
        # Temporary build location
        self._temp_build_dir: TempDirectory | None = None
        # Set to True after successful installation
        self.install_succeeded: bool | None = None
```
