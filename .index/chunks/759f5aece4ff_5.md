# Chunk: 759f5aece4ff_5

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_bdist_wheel.py`
- lines: 448-522
- chunk: 6/9

```
temp("extension_dist")
    (source_dir / "setup.py").write_text(EXTENSION_SETUPPY, encoding="utf-8")
    (source_dir / "extension.c").write_text(EXTENSION_EXAMPLE, encoding="utf-8")
    build_dir = tmp_path.joinpath("build")
    dist_dir = tmp_path.joinpath("dist")
    monkeypatch.chdir(source_dir)
    bdist_wheel_cmd(bdist_dir=str(build_dir), dist_dir=str(dist_dir)).run()


def test_build_from_readonly_tree(dummy_dist, monkeypatch, tmp_path):
    basedir = str(tmp_path.joinpath("dummy"))
    shutil.copytree(str(dummy_dist), basedir)
    monkeypatch.chdir(basedir)

    # Make the tree read-only
    for root, _dirs, files in os.walk(basedir):
        for fname in files:
            os.chmod(os.path.join(root, fname), stat.S_IREAD)

    bdist_wheel_cmd().run()


@pytest.mark.parametrize(
    ("option", "compress_type"),
    list(bdist_wheel.supported_compressions.items()),
    ids=list(bdist_wheel.supported_compressions),
)
def test_compression(dummy_dist, monkeypatch, tmp_path, option, compress_type):
    monkeypatch.chdir(dummy_dist)
    bdist_wheel_cmd(bdist_dir=str(tmp_path), compression=option).run()
    with ZipFile("dist/dummy_dist-1.0-py3-none-any.whl") as wf:
        filenames = set(wf.namelist())
        assert "dummy_dist-1.0.dist-info/RECORD" in filenames
        assert "dummy_dist-1.0.dist-info/METADATA" in filenames
        for zinfo in wf.filelist:
            assert zinfo.compress_type == compress_type


def test_wheelfile_line_endings(wheel_paths):
    for path in wheel_paths:
        with ZipFile(path) as wf:
            wheelfile = next(fn for fn in wf.filelist if fn.filename.endswith("WHEEL"))
            wheelfile_contents = wf.read(wheelfile)
            assert b"\r" not in wheelfile_contents


def test_unix_epoch_timestamps(dummy_dist, monkeypatch, tmp_path):
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "0")
    monkeypatch.chdir(dummy_dist)
    bdist_wheel_cmd(bdist_dir=str(tmp_path), build_number="2a").run()
    with ZipFile("dist/dummy_dist-1.0-2a-py3-none-any.whl") as wf:
        for zinfo in wf.filelist:
            assert zinfo.date_time >= (1980, 1, 1, 0, 0, 0)  # min epoch is used


def test_get_abi_tag_windows(monkeypatch):
    monkeypatch.setattr(tags, "interpreter_name", lambda: "cp")
    monkeypatch.setattr(sysconfig, "get_config_var", lambda x: "cp313-win_amd64")
    assert get_abi_tag() == "cp313"
    monkeypatch.setattr(sys, "gettotalrefcount", lambda: 1, False)
    assert get_abi_tag() == "cp313d"
    monkeypatch.setattr(sysconfig, "get_config_var", lambda x: "cp313t-win_amd64")
    assert get_abi_tag() == "cp313td"
    monkeypatch.delattr(sys, "gettotalrefcount")
    assert get_abi_tag() == "cp313t"


def test_get_abi_tag_pypy_old(monkeypatch):
    monkeypatch.setattr(tags, "interpreter_name", lambda: "pp")
    monkeypatch.setattr(sysconfig, "get_config_var", lambda x: "pypy36-pp73")
    assert get_abi_tag() == "pypy36_pp73"


def test_get_abi_tag_pypy_new(monkeypatch):
```
