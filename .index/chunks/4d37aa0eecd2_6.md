# Chunk: 4d37aa0eecd2_6

- source: `.venv-lab/Lib/site-packages/pip/_internal/vcs/git.py`
- lines: 485-566
- chunk: 7/8

```
         ["rev-parse", "--git-dir"],
            show_stdout=False,
            stdout_only=True,
            cwd=location,
        ).strip()
        if not os.path.isabs(git_dir):
            git_dir = os.path.join(location, git_dir)
        repo_root = os.path.abspath(os.path.join(git_dir, ".."))
        return find_path_to_project_root_from_repo_root(location, repo_root)

    @classmethod
    def get_url_rev_and_auth(cls, url: str) -> tuple[str, str | None, AuthInfo]:
        """
        Prefixes stub URLs like 'user@hostname:user/repo.git' with 'ssh://'.
        That's required because although they use SSH they sometimes don't
        work with a ssh:// scheme (e.g. GitHub). But we need a scheme for
        parsing. Hence we remove it again afterwards and return it as a stub.
        """
        # Works around an apparent Git bug
        # (see https://article.gmane.org/gmane.comp.version-control.git/146500)
        scheme, netloc, path, query, fragment = urlsplit(url)
        if scheme.endswith("file"):
            initial_slashes = path[: -len(path.lstrip("/"))]
            newpath = initial_slashes + urllib.request.url2pathname(path).replace(
                "\\", "/"
            ).lstrip("/")
            after_plus = scheme.find("+") + 1
            url = scheme[:after_plus] + urlunsplit(
                (scheme[after_plus:], netloc, newpath, query, fragment),
            )

        if "://" not in url:
            assert "file:" not in url
            url = url.replace("git+", "git+ssh://")
            url, rev, user_pass = super().get_url_rev_and_auth(url)
            url = url.replace("ssh://", "")
        else:
            url, rev, user_pass = super().get_url_rev_and_auth(url)

        return url, rev, user_pass

    @classmethod
    def update_submodules(cls, location: str, verbosity: int = 0) -> None:
        argv = ["submodule", "update", "--init", "--recursive"]

        if verbosity <= 0:
            argv.append("-q")

        if not os.path.exists(os.path.join(location, ".gitmodules")):
            return
        cls.run_command(
            argv,
            cwd=location,
        )

    @classmethod
    def get_repository_root(cls, location: str) -> str | None:
        loc = super().get_repository_root(location)
        if loc:
            return loc
        try:
            r = cls.run_command(
                ["rev-parse", "--show-toplevel"],
                cwd=location,
                show_stdout=False,
                stdout_only=True,
                on_returncode="raise",
                log_failed_cmd=False,
            )
        except BadCommand:
            logger.debug(
                "could not determine if %s is under git control "
                "because git is not available",
                location,
            )
            return None
        except InstallationError:
            return None
        return os.path.normpath(r.rstrip("\r\n"))

    @staticmethod
```
