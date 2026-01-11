# Chunk: 96bb0fa8f9fb_5

- source: `.venv-lab/Lib/site-packages/jupyterlab_server/handlers.py`
- lines: 343-359
- chunk: 6/6

```
path = ujoin(licenses_url, "(.*)")
        handlers.append(
            (licenses_path, LicensesHandler, {"manager": LicensesManager(parent=extension_app)})
        )

    # Let the lab handler act as the fallthrough option instead of a 404.
    fallthrough_url = ujoin(extension_app.app_url, r".*")
    handlers.append((fallthrough_url, NotFoundHandler))


def _camelCase(base: str) -> str:
    """Convert a string to camelCase.
    https://stackoverflow.com/a/20744956
    """
    output = "".join(x for x in base.title() if x.isalpha())
    return output[0].lower() + output[1:]
```
