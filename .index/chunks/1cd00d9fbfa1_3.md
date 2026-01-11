# Chunk: 1cd00d9fbfa1_3

- source: `.venv-lab/Lib/site-packages/pip/_internal/cli/req_command.py`
- lines: 216-296
- chunk: 4/6

```
=upgrade_strategy,
                py_version_info=py_version_info,
            )
        import pip._internal.resolution.legacy.resolver

        return pip._internal.resolution.legacy.resolver.Resolver(
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

    def get_requirements(
        self,
        args: list[str],
        options: Values,
        finder: PackageFinder,
        session: PipSession,
    ) -> list[InstallRequirement]:
        """
        Parse command-line arguments into the corresponding requirements.
        """
        requirements: list[InstallRequirement] = []

        if not should_ignore_regular_constraints(options):
            for filename in options.constraints:
                for parsed_req in parse_requirements(
                    filename,
                    constraint=True,
                    finder=finder,
                    options=options,
                    session=session,
                ):
                    req_to_add = install_req_from_parsed_requirement(
                        parsed_req,
                        isolated=options.isolated_mode,
                        user_supplied=False,
                    )
                    requirements.append(req_to_add)

        for req in args:
            req_to_add = install_req_from_line(
                req,
                comes_from=None,
                isolated=options.isolated_mode,
                user_supplied=True,
                config_settings=getattr(options, "config_settings", None),
            )
            requirements.append(req_to_add)

        if options.dependency_groups:
            for req in parse_dependency_groups(options.dependency_groups):
                req_to_add = install_req_from_req_string(
                    req,
                    isolated=options.isolated_mode,
                    user_supplied=True,
                )
                requirements.append(req_to_add)

        for req in options.editables:
            req_to_add = install_req_from_editable(
                req,
                user_supplied=True,
                isolated=options.isolated_mode,
                config_settings=getattr(options, "config_settings", None),
            )
            requirements.append(req_to_add)

        # NOTE: options.require_hashes may be set if --require-hashes is True
        for filename in options.requirements:
            for parsed_req in parse_requirements(
                filename, finder=finder, options=options, session=session
            ):
```
