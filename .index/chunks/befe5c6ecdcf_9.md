# Chunk: befe5c6ecdcf_9

- source: `.venv-lab/Lib/site-packages/pip/_internal/req/req_install.py`
- lines: 631-707
- chunk: 10/12

```
   # For editable installations
    def update_editable(self) -> None:
        if not self.link:
            logger.debug(
                "Cannot update repository at %s; repository location is unknown",
                self.source_dir,
            )
            return
        assert self.editable
        assert self.source_dir
        if self.link.scheme == "file":
            # Static paths don't get updated
            return
        vcs_backend = vcs.get_backend_for_scheme(self.link.scheme)
        # Editable requirements are validated in Requirement constructors.
        # So here, if it's neither a path nor a valid VCS URL, it's a bug.
        assert vcs_backend, f"Unsupported VCS URL {self.link.url}"
        hidden_url = hide_url(self.link.url)
        vcs_backend.obtain(self.source_dir, url=hidden_url, verbosity=0)

    # Top-level Actions
    def uninstall(
        self, auto_confirm: bool = False, verbose: bool = False
    ) -> UninstallPathSet | None:
        """
        Uninstall the distribution currently satisfying this requirement.

        Prompts before removing or modifying files unless
        ``auto_confirm`` is True.

        Refuses to delete or modify files outside of ``sys.prefix`` -
        thus uninstallation within a virtual environment can only
        modify that virtual environment, even if the virtualenv is
        linked to global site-packages.

        """
        assert self.req
        dist = get_default_environment().get_distribution(self.req.name)
        if not dist:
            logger.warning("Skipping %s as it is not installed.", self.name)
            return None
        logger.info("Found existing installation: %s", dist)

        uninstalled_pathset = UninstallPathSet.from_dist(dist)
        uninstalled_pathset.remove(auto_confirm, verbose)
        return uninstalled_pathset

    def _get_archive_name(self, path: str, parentdir: str, rootdir: str) -> str:
        def _clean_zip_name(name: str, prefix: str) -> str:
            assert name.startswith(
                prefix + os.path.sep
            ), f"name {name!r} doesn't start with prefix {prefix!r}"
            name = name[len(prefix) + 1 :]
            name = name.replace(os.path.sep, "/")
            return name

        assert self.req is not None
        path = os.path.join(parentdir, path)
        name = _clean_zip_name(path, rootdir)
        return self.req.name + "/" + name

    def archive(self, build_dir: str | None) -> None:
        """Saves archive to provided build_dir.

        Used for saving downloaded VCS requirements as part of `pip download`.
        """
        assert self.source_dir
        if build_dir is None:
            return

        create_archive = True
        archive_name = "{}-{}.zip".format(self.name, self.metadata["version"])
        archive_path = os.path.join(build_dir, archive_name)

        if os.path.exists(archive_path):
            response = ask_path_exists(
```
