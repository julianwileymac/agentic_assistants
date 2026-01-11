# Chunk: 4d37aa0eecd2_3

- source: `.venv-lab/Lib/site-packages/pip/_internal/vcs/git.py`
- lines: 250-329
- chunk: 4/8

```
d=dest,
        )
        # Change the revision to the SHA of the ref we fetched
        sha = cls.get_revision(dest, rev="FETCH_HEAD")
        rev_options = rev_options.make_new(sha)

        return rev_options

    @classmethod
    def is_commit_id_equal(cls, dest: str, name: str | None) -> bool:
        """
        Return whether the current commit hash equals the given name.

        Args:
          dest: the repository directory.
          name: a string name.
        """
        if not name:
            # Then avoid an unnecessary subprocess call.
            return False

        return cls.get_revision(dest) == name

    def fetch_new(
        self, dest: str, url: HiddenText, rev_options: RevOptions, verbosity: int
    ) -> None:
        rev_display = rev_options.to_display()
        logger.info("Cloning %s%s to %s", url, rev_display, display_path(dest))
        if verbosity <= 0:
            flags: tuple[str, ...] = ("--quiet",)
        elif verbosity == 1:
            flags = ()
        else:
            flags = ("--verbose", "--progress")
        if self.get_git_version() >= (2, 17):
            # Git added support for partial clone in 2.17
            # https://git-scm.com/docs/partial-clone
            # Speeds up cloning by functioning without a complete copy of repository
            self.run_command(
                make_command(
                    "clone",
                    "--filter=blob:none",
                    *flags,
                    url,
                    dest,
                )
            )
        else:
            self.run_command(make_command("clone", *flags, url, dest))

        if rev_options.rev:
            # Then a specific revision was requested.
            rev_options = self.resolve_revision(dest, url, rev_options)
            branch_name = getattr(rev_options, "branch_name", None)
            logger.debug("Rev options %s, branch_name %s", rev_options, branch_name)
            if branch_name is None:
                # Only do a checkout if the current commit id doesn't match
                # the requested revision.
                if not self.is_commit_id_equal(dest, rev_options.rev):
                    cmd_args = make_command(
                        "checkout",
                        "-q",
                        rev_options.to_args(),
                    )
                    self.run_command(cmd_args, cwd=dest)
            elif self.get_current_branch(dest) != branch_name:
                # Then a specific branch was requested, and that branch
                # is not yet checked out.
                track_branch = f"origin/{branch_name}"
                cmd_args = [
                    "checkout",
                    "-b",
                    branch_name,
                    "--track",
                    track_branch,
                ]
                self.run_command(cmd_args, cwd=dest)
        else:
            sha = self.get_revision(dest)
```
