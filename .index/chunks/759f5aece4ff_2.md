# Chunk: 759f5aece4ff_2

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_bdist_wheel.py`
- lines: 205-308
- chunk: 3/9

```
       name="extension", sources=["extension.c"], py_limited_api=True
                    )
                ],
            )
            """
        ),
        "setup.cfg": "[bdist_wheel]\npy_limited_api=cp32",
        "extension.c": "#define Py_LIMITED_API 0x03020000\n#include <Python.h>",
    }


def bdist_wheel_cmd(**kwargs):
    """Run command in the same process so that it is easier to collect coverage"""
    dist_obj = (
        run_setup("setup.py", stop_after="init")
        if os.path.exists("setup.py")
        else Distribution({"script_name": "%%build_meta%%"})
    )
    dist_obj.parse_config_files()
    cmd = bdist_wheel(dist_obj)
    for attr, value in kwargs.items():
        setattr(cmd, attr, value)
    cmd.finalize_options()
    return cmd


def mkexample(tmp_path_factory, name):
    basedir = tmp_path_factory.mktemp(name)
    jaraco.path.build(EXAMPLES[name], prefix=str(basedir))
    return basedir


@pytest.fixture(scope="session")
def wheel_paths(tmp_path_factory):
    build_base = tmp_path_factory.mktemp("build")
    dist_dir = tmp_path_factory.mktemp("dist")
    for name in EXAMPLES:
        example_dir = mkexample(tmp_path_factory, name)
        build_dir = build_base / name
        with jaraco.path.DirectoryStack().context(example_dir):
            bdist_wheel_cmd(bdist_dir=str(build_dir), dist_dir=str(dist_dir)).run()

    return sorted(str(fname) for fname in dist_dir.glob("*.whl"))


@pytest.fixture
def dummy_dist(tmp_path_factory):
    return mkexample(tmp_path_factory, "dummy-dist")


@pytest.fixture
def licenses_dist(tmp_path_factory):
    return mkexample(tmp_path_factory, "licenses-dist")


def test_no_scripts(wheel_paths):
    """Make sure entry point scripts are not generated."""
    path = next(path for path in wheel_paths if "complex_dist" in path)
    for entry in ZipFile(path).infolist():
        assert ".data/scripts/" not in entry.filename


def test_unicode_record(wheel_paths):
    path = next(path for path in wheel_paths if "unicode_dist" in path)
    with ZipFile(path) as zf:
        record = zf.read("unicode_dist-0.1.dist-info/RECORD")

    assert "åäö_日本語.py".encode() in record


UTF8_PKG_INFO = """\
Metadata-Version: 2.1
Name: helloworld
Version: 42
Author-email: "John X. Ãørçeč" <john@utf8.org>, Γαμα קּ 東 <gama@utf8.org>


UTF-8 描述 説明
"""


def test_preserve_unicode_metadata(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    egginfo = tmp_path / "dummy_dist.egg-info"
    distinfo = tmp_path / "dummy_dist.dist-info"

    egginfo.mkdir()
    (egginfo / "PKG-INFO").write_text(UTF8_PKG_INFO, encoding="utf-8")
    (egginfo / "dependency_links.txt").touch()

    class simpler_bdist_wheel(bdist_wheel):
        """Avoid messing with setuptools/distutils internals"""

        def __init__(self):
            pass

        @property
        def license_paths(self):
            return []

    cmd_obj = simpler_bdist_wheel()
    cmd_obj.egg2dist(egginfo, distinfo)
```
