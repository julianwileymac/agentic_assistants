# Chunk: 4d37aa0eecd2_5

- source: `.venv-lab/Lib/site-packages/pip/_internal/vcs/git.py`
- lines: 406-493
- chunk: 6/8

```
   try:
            found_remote = remotes[0]
        except IndexError:
            raise RemoteNotFoundError

        for remote in remotes:
            if remote.startswith("remote.origin.url "):
                found_remote = remote
                break
        url = found_remote.split(" ")[1]
        return cls._git_remote_to_pip_url(url.strip())

    @staticmethod
    def _git_remote_to_pip_url(url: str) -> str:
        """
        Convert a remote url from what git uses to what pip accepts.

        There are 3 legal forms **url** may take:

            1. A fully qualified url: ssh://git@example.com/foo/bar.git
            2. A local project.git folder: /path/to/bare/repository.git
            3. SCP shorthand for form 1: git@example.com:foo/bar.git

        Form 1 is output as-is. Form 2 must be converted to URI and form 3 must
        be converted to form 1.

        See the corresponding test test_git_remote_url_to_pip() for examples of
        sample inputs/outputs.
        """
        if re.match(r"\w+://", url):
            # This is already valid. Pass it though as-is.
            return url
        if os.path.exists(url):
            # A local bare remote (git clone --mirror).
            # Needs a file:// prefix.
            return pathlib.PurePath(url).as_uri()
        scp_match = SCP_REGEX.match(url)
        if scp_match:
            # Add an ssh:// prefix and replace the ':' with a '/'.
            return scp_match.expand(r"ssh://\1\2/\3")
        # Otherwise, bail out.
        raise RemoteNotValidError(url)

    @classmethod
    def has_commit(cls, location: str, rev: str) -> bool:
        """
        Check if rev is a commit that is available in the local repository.
        """
        try:
            cls.run_command(
                ["rev-parse", "-q", "--verify", "sha^" + rev],
                cwd=location,
                log_failed_cmd=False,
            )
        except InstallationError:
            return False
        else:
            return True

    @classmethod
    def get_revision(cls, location: str, rev: str | None = None) -> str:
        if rev is None:
            rev = "HEAD"
        current_rev = cls.run_command(
            ["rev-parse", rev],
            show_stdout=False,
            stdout_only=True,
            cwd=location,
        )
        return current_rev.strip()

    @classmethod
    def get_subdirectory(cls, location: str) -> str | None:
        """
        Return the path to Python project root, relative to the repo root.
        Return None if the project root is in the repo root.
        """
        # find the repo root
        git_dir = cls.run_command(
            ["rev-parse", "--git-dir"],
            show_stdout=False,
            stdout_only=True,
            cwd=location,
        ).strip()
        if not os.path.isabs(git_dir):
            git_dir = os.path.join(location, git_dir)
        repo_root = os.path.abspath(os.path.join(git_dir, ".."))
```
