# Chunk: 759f5aece4ff_3

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_bdist_wheel.py`
- lines: 295-374
- chunk: 4/9

```
ass simpler_bdist_wheel(bdist_wheel):
        """Avoid messing with setuptools/distutils internals"""

        def __init__(self):
            pass

        @property
        def license_paths(self):
            return []

    cmd_obj = simpler_bdist_wheel()
    cmd_obj.egg2dist(egginfo, distinfo)

    metadata = (distinfo / "METADATA").read_text(encoding="utf-8")
    assert 'Author-email: "John X. Ãørçeč"' in metadata
    assert "Γαμα קּ 東 " in metadata
    assert "UTF-8 描述 説明" in metadata


def test_licenses_default(dummy_dist, monkeypatch, tmp_path):
    monkeypatch.chdir(dummy_dist)
    bdist_wheel_cmd(bdist_dir=str(tmp_path)).run()
    with ZipFile("dist/dummy_dist-1.0-py3-none-any.whl") as wf:
        license_files = {
            "dummy_dist-1.0.dist-info/licenses/" + fname
            for fname in DEFAULT_LICENSE_FILES
        }
        assert set(wf.namelist()) == DEFAULT_FILES | license_files


def test_licenses_deprecated(dummy_dist, monkeypatch, tmp_path):
    dummy_dist.joinpath("setup.cfg").write_text(
        "[metadata]\nlicense_file=licenses_dir/DUMMYFILE", encoding="utf-8"
    )
    monkeypatch.chdir(dummy_dist)

    bdist_wheel_cmd(bdist_dir=str(tmp_path)).run()

    with ZipFile("dist/dummy_dist-1.0-py3-none-any.whl") as wf:
        license_files = {"dummy_dist-1.0.dist-info/licenses/licenses_dir/DUMMYFILE"}
        assert set(wf.namelist()) == DEFAULT_FILES | license_files


@pytest.mark.parametrize(
    ("config_file", "config"),
    [
        ("setup.cfg", "[metadata]\nlicense_files=licenses_dir/*\n  LICENSE"),
        ("setup.cfg", "[metadata]\nlicense_files=licenses_dir/*, LICENSE"),
        (
            "setup.py",
            SETUPPY_EXAMPLE.replace(
                ")", "  license_files=['licenses_dir/DUMMYFILE', 'LICENSE'])"
            ),
        ),
    ],
)
def test_licenses_override(dummy_dist, monkeypatch, tmp_path, config_file, config):
    dummy_dist.joinpath(config_file).write_text(config, encoding="utf-8")
    monkeypatch.chdir(dummy_dist)
    bdist_wheel_cmd(bdist_dir=str(tmp_path)).run()
    with ZipFile("dist/dummy_dist-1.0-py3-none-any.whl") as wf:
        license_files = {
            "dummy_dist-1.0.dist-info/licenses/" + fname
            for fname in {"licenses_dir/DUMMYFILE", "LICENSE"}
        }
        assert set(wf.namelist()) == DEFAULT_FILES | license_files
        metadata = wf.read("dummy_dist-1.0.dist-info/METADATA").decode("utf8")
        assert "License-File: licenses_dir/DUMMYFILE" in metadata
        assert "License-File: LICENSE" in metadata


def test_licenses_preserve_folder_structure(licenses_dist, monkeypatch, tmp_path):
    monkeypatch.chdir(licenses_dist)
    bdist_wheel_cmd(bdist_dir=str(tmp_path)).run()
    print(os.listdir("dist"))
    with ZipFile("dist/licenses_dist-1.0-py3-none-any.whl") as wf:
        default_files = {name.replace("dummy_", "licenses_") for name in DEFAULT_FILES}
        license_files = {
            "licenses_dist-1.0.dist-info/licenses/LICENSE",
```
