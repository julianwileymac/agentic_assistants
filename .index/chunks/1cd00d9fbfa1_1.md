# Chunk: 1cd00d9fbfa1_1

- source: `.venv-lab/Lib/site-packages/pip/_internal/cli/req_command.py`
- lines: 77-159
- chunk: 2/6

```
try.set_delete(t, False)

    def wrapper(self: _CommandT, options: Values, args: list[str]) -> int:
        assert self.tempdir_registry is not None
        if options.no_clean:
            configure_tempdir_registry(self.tempdir_registry)

        try:
            return func(self, options, args)
        except PreviousBuildDirError:
            # This kind of conflict can occur when the user passes an explicit
            # build directory with a pre-existing folder. In that case we do
            # not want to accidentally remove it.
            configure_tempdir_registry(self.tempdir_registry)
            raise

    return wrapper


class RequirementCommand(IndexGroupCommand):
    def __init__(self, *args: Any, **kw: Any) -> None:
        super().__init__(*args, **kw)

        self.cmd_opts.add_option(cmdoptions.dependency_groups())
        self.cmd_opts.add_option(cmdoptions.no_clean())

    @staticmethod
    def determine_resolver_variant(options: Values) -> str:
        """Determines which resolver should be used, based on the given options."""
        if "legacy-resolver" in options.deprecated_features_enabled:
            return "legacy"

        return "resolvelib"

    @classmethod
    def make_requirement_preparer(
        cls,
        temp_build_dir: TempDirectory,
        options: Values,
        build_tracker: BuildTracker,
        session: PipSession,
        finder: PackageFinder,
        use_user_site: bool,
        download_dir: str | None = None,
        verbosity: int = 0,
    ) -> RequirementPreparer:
        """
        Create a RequirementPreparer instance for the given parameters.
        """
        temp_build_dir_path = temp_build_dir.path
        assert temp_build_dir_path is not None
        legacy_resolver = False

        resolver_variant = cls.determine_resolver_variant(options)
        if resolver_variant == "resolvelib":
            lazy_wheel = "fast-deps" in options.features_enabled
            if lazy_wheel:
                logger.warning(
                    "pip is using lazily downloaded wheels using HTTP "
                    "range requests to obtain dependency information. "
                    "This experimental feature is enabled through "
                    "--use-feature=fast-deps and it is not ready for "
                    "production."
                )
        else:
            legacy_resolver = True
            lazy_wheel = False
            if "fast-deps" in options.features_enabled:
                logger.warning(
                    "fast-deps has no effect when used with the legacy resolver."
                )

        # Handle build constraints
        build_constraints = getattr(options, "build_constraints", [])
        build_constraint_feature_enabled = (
            "build-constraint" in options.features_enabled
        )

        return RequirementPreparer(
            build_dir=temp_build_dir_path,
            src_dir=options.src_dir,
            download_dir=download_dir,
```
