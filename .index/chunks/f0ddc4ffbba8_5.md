# Chunk: f0ddc4ffbba8_5

- source: `.venv-lab/Lib/site-packages/jupyter_client/adapter.py`
- lines: 391-433
- chunk: 6/6

```
    return msg


def adapt(msg: dict[str, Any], to_version: int = protocol_version_info[0]) -> dict[str, Any]:
    """Adapt a single message to a target version

    Parameters
    ----------

    msg : dict
        A Jupyter message.
    to_version : int, optional
        The target major version.
        If unspecified, adapt to the current version.

    Returns
    -------

    msg : dict
        A Jupyter message appropriate in the new version.
    """
    from .session import utcnow

    header = msg["header"]
    if "date" not in header:
        header["date"] = utcnow()
    if "version" in header:
        from_version = int(header["version"].split(".")[0])
    else:
        # assume last version before adding the key to the header
        from_version = 4
    adapter = adapters.get((from_version, to_version), None)
    if adapter is None:
        return msg
    return adapter(msg)


# one adapter per major version from,to
adapters = {
    (5, 4): V5toV4(),
    (4, 5): V4toV5(),
}
```
