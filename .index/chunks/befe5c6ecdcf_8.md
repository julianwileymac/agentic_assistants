# Chunk: befe5c6ecdcf_8

- source: `.venv-lab/Lib/site-packages/pip/_internal/req/req_install.py`
- lines: 562-640
- chunk: 9/12

```
local_file_path),
                canonicalize_name(self.req.name),
            )
        raise AssertionError(
            f"InstallRequirement {self} has no metadata directory and no wheel: "
            f"can't make a distribution."
        )

    def assert_source_matches_version(self) -> None:
        assert self.source_dir, f"No source dir for {self}"
        version = self.metadata["version"]
        if self.req and self.req.specifier and version not in self.req.specifier:
            logger.warning(
                "Requested %s, but installing version %s",
                self,
                version,
            )
        else:
            logger.debug(
                "Source in %s has version %s, which satisfies requirement %s",
                display_path(self.source_dir),
                version,
                self,
            )

    # For both source distributions and editables
    def ensure_has_source_dir(
        self,
        parent_dir: str,
        autodelete: bool = False,
        parallel_builds: bool = False,
    ) -> None:
        """Ensure that a source_dir is set.

        This will create a temporary build dir if the name of the requirement
        isn't known yet.

        :param parent_dir: The ideal pip parent_dir for the source_dir.
            Generally src_dir for editables and build_dir for sdists.
        :return: self.source_dir
        """
        if self.source_dir is None:
            self.source_dir = self.ensure_build_location(
                parent_dir,
                autodelete=autodelete,
                parallel_builds=parallel_builds,
            )

    def needs_unpacked_archive(self, archive_source: Path) -> None:
        assert self._archive_source is None
        self._archive_source = archive_source

    def ensure_pristine_source_checkout(self) -> None:
        """Ensure the source directory has not yet been built in."""
        assert self.source_dir is not None
        if self._archive_source is not None:
            unpack_file(str(self._archive_source), self.source_dir)
        elif is_installable_dir(self.source_dir):
            # If a checkout exists, it's unwise to keep going.
            # version inconsistencies are logged later, but do not fail
            # the installation.
            raise PreviousBuildDirError(
                f"pip can't proceed with requirements '{self}' due to a "
                f"pre-existing build directory ({self.source_dir}). This is likely "
                "due to a previous installation that failed . pip is "
                "being responsible and not assuming it can delete this. "
                "Please delete it and try again."
            )

    # For editable installations
    def update_editable(self) -> None:
        if not self.link:
            logger.debug(
                "Cannot update repository at %s; repository location is unknown",
                self.source_dir,
            )
            return
        assert self.editable
```
