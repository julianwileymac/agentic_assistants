# Chunk: 4d37aa0eecd2_7

- source: `.venv-lab/Lib/site-packages/pip/_internal/vcs/git.py`
- lines: 556-572
- chunk: 8/8

```
           "could not determine if %s is under git control "
                "because git is not available",
                location,
            )
            return None
        except InstallationError:
            return None
        return os.path.normpath(r.rstrip("\r\n"))

    @staticmethod
    def should_add_vcs_url_prefix(repo_url: str) -> bool:
        """In either https or ssh form, requirements must be prefixed with git+."""
        return True


vcs.register(Git)
```
