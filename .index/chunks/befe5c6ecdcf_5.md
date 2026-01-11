# Chunk: befe5c6ecdcf_5

- source: `.venv-lab/Lib/site-packages/pip/_internal/req/req_install.py`
- lines: 345-426
- chunk: 6/12

```
 name so multiple builds do not interfere with each other.
        dir_name: str = canonicalize_name(self.req.name)
        if parallel_builds:
            dir_name = f"{dir_name}_{uuid.uuid4().hex}"

        # FIXME: Is there a better place to create the build_dir? (hg and bzr
        # need this)
        if not os.path.exists(build_dir):
            logger.debug("Creating directory %s", build_dir)
            os.makedirs(build_dir)
        actual_build_dir = os.path.join(build_dir, dir_name)
        # `None` indicates that we respect the globally-configured deletion
        # settings, which is what we actually want when auto-deleting.
        delete_arg = None if autodelete else False
        return TempDirectory(
            path=actual_build_dir,
            delete=delete_arg,
            kind=tempdir_kinds.REQ_BUILD,
            globally_managed=True,
        ).path

    def _set_requirement(self) -> None:
        """Set requirement after generating metadata."""
        assert self.req is None
        assert self.metadata is not None
        assert self.source_dir is not None

        # Construct a Requirement object from the generated metadata
        if isinstance(parse_version(self.metadata["Version"]), Version):
            op = "=="
        else:
            op = "==="

        self.req = get_requirement(
            "".join(
                [
                    self.metadata["Name"],
                    op,
                    self.metadata["Version"],
                ]
            )
        )

    def warn_on_mismatching_name(self) -> None:
        assert self.req is not None
        metadata_name = canonicalize_name(self.metadata["Name"])
        if canonicalize_name(self.req.name) == metadata_name:
            # Everything is fine.
            return

        # If we're here, there's a mismatch. Log a warning about it.
        logger.warning(
            "Generating metadata for package %s "
            "produced metadata for project name %s. Fix your "
            "#egg=%s fragments.",
            self.name,
            metadata_name,
            self.name,
        )
        self.req = get_requirement(metadata_name)

    def check_if_exists(self, use_user_site: bool) -> None:
        """Find an installed distribution that satisfies or conflicts
        with this requirement, and set self.satisfied_by or
        self.should_reinstall appropriately.
        """
        if self.req is None:
            return
        existing_dist = get_default_environment().get_distribution(self.req.name)
        if not existing_dist:
            return

        version_compatible = self.req.specifier.contains(
            existing_dist.version,
            prereleases=True,
        )
        if not version_compatible:
            self.satisfied_by = None
            if use_user_site:
                if existing_dist.in_usersite:
                    self.should_reinstall = True
```
