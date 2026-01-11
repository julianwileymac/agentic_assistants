# Chunk: befe5c6ecdcf_7

- source: `.venv-lab/Lib/site-packages/pip/_internal/req/req_install.py`
- lines: 489-571
- chunk: 8/12

```
end = ConfiguredBuildBackendHookCaller(
            self,
            self.unpacked_source_directory,
            backend,
            backend_path=backend_path,
        )

    def editable_sanity_check(self) -> None:
        """Check that an editable requirement if valid for use with PEP 517/518.

        This verifies that an editable has a build backend that supports PEP 660.
        """
        if self.editable and not self.supports_pyproject_editable:
            raise InstallationError(
                f"Project {self} uses a build backend "
                f"that is missing the 'build_editable' hook, so "
                f"it cannot be installed in editable mode. "
                f"Consider using a build backend that supports PEP 660."
            )

    def prepare_metadata(self) -> None:
        """Ensure that project metadata is available.

        Under PEP 517 and PEP 660, call the backend hook to prepare the metadata.
        Under legacy processing, call setup.py egg-info.
        """
        assert self.source_dir, f"No source dir for {self}"
        details = self.name or f"from {self.link}"

        assert self.pep517_backend is not None
        if (
            self.editable
            and self.permit_editable_wheels
            and self.supports_pyproject_editable
        ):
            self.metadata_directory = generate_editable_metadata(
                build_env=self.build_env,
                backend=self.pep517_backend,
                details=details,
            )
        else:
            self.metadata_directory = generate_metadata(
                build_env=self.build_env,
                backend=self.pep517_backend,
                details=details,
            )

        # Act on the newly generated metadata, based on the name and version.
        if not self.name:
            self._set_requirement()
        else:
            self.warn_on_mismatching_name()

        self.assert_source_matches_version()

    @property
    def metadata(self) -> Any:
        if not hasattr(self, "_metadata"):
            self._metadata = self.get_dist().metadata

        return self._metadata

    def set_dist(self, distribution: BaseDistribution) -> None:
        self._distribution = distribution

    def get_dist(self) -> BaseDistribution:
        if self._distribution is not None:
            return self._distribution
        elif self.metadata_directory:
            return get_directory_distribution(self.metadata_directory)
        elif self.local_file_path and self.is_wheel:
            assert self.req is not None
            return get_wheel_distribution(
                FilesystemWheel(self.local_file_path),
                canonicalize_name(self.req.name),
            )
        raise AssertionError(
            f"InstallRequirement {self} has no metadata directory and no wheel: "
            f"can't make a distribution."
        )

    def assert_source_matches_version(self) -> None:
```
