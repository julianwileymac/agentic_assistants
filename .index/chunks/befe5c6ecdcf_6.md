# Chunk: befe5c6ecdcf_6

- source: `.venv-lab/Lib/site-packages/pip/_internal/req/req_install.py`
- lines: 417-499
- chunk: 7/12

```
elf.req.specifier.contains(
            existing_dist.version,
            prereleases=True,
        )
        if not version_compatible:
            self.satisfied_by = None
            if use_user_site:
                if existing_dist.in_usersite:
                    self.should_reinstall = True
                elif running_under_virtualenv() and existing_dist.in_site_packages:
                    raise InstallationError(
                        f"Will not install to the user site because it will "
                        f"lack sys.path precedence to {existing_dist.raw_name} "
                        f"in {existing_dist.location}"
                    )
            else:
                self.should_reinstall = True
        else:
            if self.editable:
                self.should_reinstall = True
                # when installing editables, nothing pre-existing should ever
                # satisfy
                self.satisfied_by = None
            else:
                self.satisfied_by = existing_dist

    # Things valid for wheels
    @property
    def is_wheel(self) -> bool:
        if not self.link:
            return False
        return self.link.is_wheel

    @property
    def is_wheel_from_cache(self) -> bool:
        # When True, it means that this InstallRequirement is a local wheel file in the
        # cache of locally built wheels.
        return self.cached_wheel_source_link is not None

    # Things valid for sdists
    @property
    def unpacked_source_directory(self) -> str:
        assert self.source_dir, f"No source dir for {self}"
        return os.path.join(
            self.source_dir, self.link and self.link.subdirectory_fragment or ""
        )

    @property
    def setup_py_path(self) -> str:
        assert self.source_dir, f"No source dir for {self}"
        setup_py = os.path.join(self.unpacked_source_directory, "setup.py")

        return setup_py

    @property
    def pyproject_toml_path(self) -> str:
        assert self.source_dir, f"No source dir for {self}"
        return make_pyproject_path(self.unpacked_source_directory)

    def load_pyproject_toml(self) -> None:
        """Load the pyproject.toml file.

        After calling this routine, all of the attributes related to PEP 517
        processing for this requirement have been set.
        """
        pyproject_toml_data = load_pyproject_toml(
            self.pyproject_toml_path, self.setup_py_path, str(self)
        )
        assert pyproject_toml_data
        requires, backend, check, backend_path = pyproject_toml_data
        self.requirements_to_check = check
        self.pyproject_requires = requires
        self.pep517_backend = ConfiguredBuildBackendHookCaller(
            self,
            self.unpacked_source_directory,
            backend,
            backend_path=backend_path,
        )

    def editable_sanity_check(self) -> None:
        """Check that an editable requirement if valid for use with PEP 517/518.
```
