# Chunk: 0ac3a286abdb_1

- source: `.venv-lab/Lib/site-packages/pip/_internal/commands/uninstall.py`
- lines: 82-114
- chunk: 2/2

```
r filename in options.requirements:
            for parsed_req in parse_requirements(
                filename, options=options, session=session
            ):
                req = install_req_from_parsed_requirement(
                    parsed_req, isolated=options.isolated_mode
                )
                if req.name:
                    reqs_to_uninstall[canonicalize_name(req.name)] = req
        if not reqs_to_uninstall:
            raise InstallationError(
                f"You must give at least one requirement to {self.name} (see "
                f'"pip help {self.name}")'
            )

        if not options.override_externally_managed:
            check_externally_managed()

        protect_pip_from_modification_on_windows(
            modifying_pip="pip" in reqs_to_uninstall
        )

        for req in reqs_to_uninstall.values():
            uninstall_pathset = req.uninstall(
                auto_confirm=options.yes,
                verbose=self.verbosity > 0,
            )
            if uninstall_pathset:
                uninstall_pathset.commit()
        if options.root_user_action == "warn":
            warn_if_run_as_root()
        return SUCCESS
```
