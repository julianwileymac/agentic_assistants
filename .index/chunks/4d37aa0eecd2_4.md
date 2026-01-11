# Chunk: 4d37aa0eecd2_4

- source: `.venv-lab/Lib/site-packages/pip/_internal/vcs/git.py`
- lines: 319-416
- chunk: 5/8

```
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
            rev_options = rev_options.make_new(sha)

        logger.info("Resolved %s to commit %s", url, rev_options.rev)

        #: repo may contain submodules
        self.update_submodules(dest, verbosity=verbosity)

    def switch(
        self,
        dest: str,
        url: HiddenText,
        rev_options: RevOptions,
        verbosity: int = 0,
    ) -> None:
        self.run_command(
            make_command("config", "remote.origin.url", url),
            cwd=dest,
        )

        extra_flags = []

        if verbosity <= 0:
            extra_flags.append("-q")

        cmd_args = make_command("checkout", *extra_flags, rev_options.to_args())
        self.run_command(cmd_args, cwd=dest)

        self.update_submodules(dest, verbosity=verbosity)

    def update(
        self,
        dest: str,
        url: HiddenText,
        rev_options: RevOptions,
        verbosity: int = 0,
    ) -> None:
        extra_flags = []

        if verbosity <= 0:
            extra_flags.append("-q")

        # First fetch changes from the default remote
        if self.get_git_version() >= (1, 9):
            # fetch tags in addition to everything else
            self.run_command(["fetch", "--tags", *extra_flags], cwd=dest)
        else:
            self.run_command(["fetch", *extra_flags], cwd=dest)
        # Then reset to wanted revision (maybe even origin/master)
        rev_options = self.resolve_revision(dest, url, rev_options)
        cmd_args = make_command(
            "reset",
            "--hard",
            *extra_flags,
            rev_options.to_args(),
        )
        self.run_command(cmd_args, cwd=dest)
        #: update submodules
        self.update_submodules(dest, verbosity=verbosity)

    @classmethod
    def get_remote_url(cls, location: str) -> str:
        """
        Return URL of the first remote encountered.

        Raises RemoteNotFoundError if the repository does not have a remote
        url configured.
        """
        # We need to pass 1 for extra_ok_returncodes since the command
        # exits with return code 1 if there are no matching lines.
        stdout = cls.run_command(
            ["config", "--get-regexp", r"remote\..*\.url"],
            extra_ok_returncodes=(1,),
            show_stdout=False,
            stdout_only=True,
            cwd=location,
        )
        remotes = stdout.splitlines()
        try:
            found_remote = remotes[0]
        except IndexError:
            raise RemoteNotFoundError

        for remote in remotes:
            if remote.startswith("remote.origin.url "):
                found_remote = remote
                break
        url = found_remote.split(" ")[1]
```
