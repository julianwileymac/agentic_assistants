# Chunk: bdb549e7f2ec_7

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_core_metadata.py`
- lines: 560-623
- chunk: 8/8

```
h()
        regenerated = buffer.getvalue()

    raw_metadata = bytes(metadata, "utf-8")
    # Normalise newlines to avoid test errors on Windows:
    raw_metadata = b"\n".join(raw_metadata.splitlines())
    regenerated = b"\n".join(regenerated.splitlines())
    assert regenerated == raw_metadata


def _normalize_metadata(msg: Message) -> str:
    """Allow equivalent metadata to be compared directly"""
    # The main challenge regards the requirements and extras.
    # Both setuptools and wheel already apply some level of normalization
    # but they differ regarding which character is chosen, according to the
    # following spec it should be "-":
    # https://packaging.python.org/en/latest/specifications/name-normalization/

    # Related issues:
    # https://github.com/pypa/packaging/issues/845
    # https://github.com/pypa/packaging/issues/644#issuecomment-2429813968

    extras = {x.replace("_", "-"): x for x in msg.get_all("Provides-Extra", [])}
    reqs = [
        _normalize_req(req, extras)
        for req in _reqs.parse(msg.get_all("Requires-Dist", []))
    ]
    del msg["Requires-Dist"]
    del msg["Provides-Extra"]

    # Ensure consistent ord
    for req in sorted(reqs):
        msg["Requires-Dist"] = req
    for extra in sorted(extras):
        msg["Provides-Extra"] = extra

    # TODO: Handle lack of PEP 643 implementation in pypa/wheel?
    del msg["Metadata-Version"]

    return msg.as_string()


def _normalize_req(req: Requirement, extras: dict[str, str]) -> str:
    """Allow equivalent requirement objects to be compared directly"""
    as_str = str(req).replace(req.name, req.name.replace("_", "-"))
    for norm, orig in extras.items():
        as_str = as_str.replace(orig, norm)
    return as_str


def _get_pkginfo(dist: Distribution):
    with io.StringIO() as fp:
        dist.metadata.write_pkg_file(fp)
        return fp.getvalue()


def _get_metadata(dist: Distribution | None = None):
    return message_from_string(_get_pkginfo(dist or _makedist()))


def _valid_metadata(text: str) -> bool:
    metadata = Metadata.from_email(text, validate=True)  # can raise exceptions
    return metadata is not None
```
