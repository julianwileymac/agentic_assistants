# Chunk: befe5c6ecdcf_11

- source: `.venv-lab/Lib/site-packages/pip/_internal/req/req_install.py`
- lines: 771-829
- chunk: 12/12

```
e,
            home=home,
            root=root,
            isolated=self.isolated,
            prefix=prefix,
        )

        assert self.is_wheel
        assert self.local_file_path

        install_wheel(
            self.req.name,
            self.local_file_path,
            scheme=scheme,
            req_description=str(self.req),
            pycompile=pycompile,
            warn_script_location=warn_script_location,
            direct_url=self.download_info if self.is_direct else None,
            requested=self.user_supplied,
        )
        self.install_succeeded = True


def check_invalid_constraint_type(req: InstallRequirement) -> str:
    # Check for unsupported forms
    problem = ""
    if not req.name:
        problem = "Unnamed requirements are not allowed as constraints"
    elif req.editable:
        problem = "Editable requirements are not allowed as constraints"
    elif req.extras:
        problem = "Constraints cannot have extras"

    if problem:
        deprecated(
            reason=(
                "Constraints are only allowed to take the form of a package "
                "name and a version specifier. Other forms were originally "
                "permitted as an accident of the implementation, but were "
                "undocumented. The new implementation of the resolver no "
                "longer supports these forms."
            ),
            replacement="replacing the constraint with a requirement",
            # No plan yet for when the new resolver becomes default
            gone_in=None,
            issue=8210,
        )

    return problem


def _has_option(options: Values, reqs: list[InstallRequirement], option: str) -> bool:
    if getattr(options, option, None):
        return True
    for req in reqs:
        if getattr(req, option, None):
            return True
    return False
```
