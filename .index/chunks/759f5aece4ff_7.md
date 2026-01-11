# Chunk: 759f5aece4ff_7

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_bdist_wheel.py`
- lines: 591-673
- chunk: 8/9

```
tries

    for not_expected in (
        "test.data/headers/hello.h",
        "test-1.0.data/data/hello/world/file.txt",
        "test.dist-info/METADATA",
        "test-1.0.dist-info/WHEEL",
    ):
        assert not_expected not in entries


@pytest.mark.parametrize(
    ("reported", "expected"),
    [("linux-x86_64", "linux_i686"), ("linux-aarch64", "linux_armv7l")],
)
@pytest.mark.skipif(
    platform.system() != "Linux", reason="Only makes sense to test on Linux"
)
def test_platform_linux32(reported, expected, monkeypatch):
    monkeypatch.setattr(struct, "calcsize", lambda x: 4)
    dist = setuptools.Distribution()
    cmd = bdist_wheel(dist)
    cmd.plat_name = reported
    cmd.root_is_pure = False
    _, _, actual = cmd.get_tag()
    assert actual == expected


def test_no_ctypes(monkeypatch) -> None:
    def _fake_import(name: str, *args, **kwargs):
        if name == "ctypes":
            raise ModuleNotFoundError(f"No module named {name}")

        return importlib.__import__(name, *args, **kwargs)

    with suppress(KeyError):
        monkeypatch.delitem(sys.modules, "wheel.macosx_libfile")

    # Install an importer shim that refuses to load ctypes
    monkeypatch.setattr(builtins, "__import__", _fake_import)
    with pytest.raises(ModuleNotFoundError, match="No module named ctypes"):
        import wheel.macosx_libfile  # noqa: F401

    # Unload and reimport the bdist_wheel command module to make sure it won't try to
    # import ctypes
    monkeypatch.delitem(sys.modules, "setuptools.command.bdist_wheel")

    import setuptools.command.bdist_wheel  # noqa: F401


def test_dist_info_provided(dummy_dist, monkeypatch, tmp_path):
    monkeypatch.chdir(dummy_dist)
    distinfo = tmp_path / "dummy_dist.dist-info"

    distinfo.mkdir()
    (distinfo / "METADATA").write_text("name: helloworld", encoding="utf-8")

    # We don't control the metadata. According to PEP-517, "The hook MAY also
    # create other files inside this directory, and a build frontend MUST
    # preserve".
    (distinfo / "FOO").write_text("bar", encoding="utf-8")

    bdist_wheel_cmd(bdist_dir=str(tmp_path), dist_info_dir=str(distinfo)).run()
    expected = {
        "dummy_dist-1.0.dist-info/FOO",
        "dummy_dist-1.0.dist-info/RECORD",
    }
    with ZipFile("dist/dummy_dist-1.0-py3-none-any.whl") as wf:
        files_found = set(wf.namelist())
    # Check that all expected files are there.
    assert expected - files_found == set()
    # Make sure there is no accidental egg-info bleeding into the wheel.
    assert not [path for path in files_found if 'egg-info' in str(path)]


def test_allow_grace_period_parent_directory_license(monkeypatch, tmp_path):
    # Motivation: https://github.com/pypa/setuptools/issues/4892
    # TODO: Remove this test after deprecation period is over
    files = {
        "LICENSE.txt": "parent license",  # <---- the license files are outside
        "NOTICE.txt": "parent notice",
        "python": {
```
