# Chunk: 1cd00d9fbfa1_2

- source: `.venv-lab/Lib/site-packages/pip/_internal/cli/req_command.py`
- lines: 150-225
- chunk: 3/6

```
ons, "build_constraints", [])
        build_constraint_feature_enabled = (
            "build-constraint" in options.features_enabled
        )

        return RequirementPreparer(
            build_dir=temp_build_dir_path,
            src_dir=options.src_dir,
            download_dir=download_dir,
            build_isolation=options.build_isolation,
            build_isolation_installer=SubprocessBuildEnvironmentInstaller(
                finder,
                build_constraints=build_constraints,
                build_constraint_feature_enabled=build_constraint_feature_enabled,
            ),
            check_build_deps=options.check_build_deps,
            build_tracker=build_tracker,
            session=session,
            progress_bar=options.progress_bar,
            finder=finder,
            require_hashes=options.require_hashes,
            use_user_site=use_user_site,
            lazy_wheel=lazy_wheel,
            verbosity=verbosity,
            legacy_resolver=legacy_resolver,
            resume_retries=options.resume_retries,
        )

    @classmethod
    def make_resolver(
        cls,
        preparer: RequirementPreparer,
        finder: PackageFinder,
        options: Values,
        wheel_cache: WheelCache | None = None,
        use_user_site: bool = False,
        ignore_installed: bool = True,
        ignore_requires_python: bool = False,
        force_reinstall: bool = False,
        upgrade_strategy: str = "to-satisfy-only",
        py_version_info: tuple[int, ...] | None = None,
    ) -> BaseResolver:
        """
        Create a Resolver instance for the given parameters.
        """
        make_install_req = partial(
            install_req_from_req_string,
            isolated=options.isolated_mode,
        )
        resolver_variant = cls.determine_resolver_variant(options)
        # The long import name and duplicated invocation is needed to convince
        # Mypy into correctly typechecking. Otherwise it would complain the
        # "Resolver" class being redefined.
        if resolver_variant == "resolvelib":
            import pip._internal.resolution.resolvelib.resolver

            return pip._internal.resolution.resolvelib.resolver.Resolver(
                preparer=preparer,
                finder=finder,
                wheel_cache=wheel_cache,
                make_install_req=make_install_req,
                use_user_site=use_user_site,
                ignore_dependencies=options.ignore_dependencies,
                ignore_installed=ignore_installed,
                ignore_requires_python=ignore_requires_python,
                force_reinstall=force_reinstall,
                upgrade_strategy=upgrade_strategy,
                py_version_info=py_version_info,
            )
        import pip._internal.resolution.legacy.resolver

        return pip._internal.resolution.legacy.resolver.Resolver(
            preparer=preparer,
            finder=finder,
            wheel_cache=wheel_cache,
```
