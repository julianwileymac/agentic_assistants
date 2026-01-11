# Chunk: 759f5aece4ff_4

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_bdist_wheel.py`
- lines: 368-454
- chunk: 5/9

```
ist_dir=str(tmp_path)).run()
    print(os.listdir("dist"))
    with ZipFile("dist/licenses_dist-1.0-py3-none-any.whl") as wf:
        default_files = {name.replace("dummy_", "licenses_") for name in DEFAULT_FILES}
        license_files = {
            "licenses_dist-1.0.dist-info/licenses/LICENSE",
            "licenses_dist-1.0.dist-info/licenses/src/vendor/LICENSE",
        }
        assert set(wf.namelist()) == default_files | license_files
        metadata = wf.read("licenses_dist-1.0.dist-info/METADATA").decode("utf8")
        assert "License-File: src/vendor/LICENSE" in metadata
        assert "License-File: LICENSE" in metadata


def test_licenses_disabled(dummy_dist, monkeypatch, tmp_path):
    dummy_dist.joinpath("setup.cfg").write_text(
        "[metadata]\nlicense_files=\n", encoding="utf-8"
    )
    monkeypatch.chdir(dummy_dist)
    bdist_wheel_cmd(bdist_dir=str(tmp_path)).run()
    with ZipFile("dist/dummy_dist-1.0-py3-none-any.whl") as wf:
        assert set(wf.namelist()) == DEFAULT_FILES


def test_build_number(dummy_dist, monkeypatch, tmp_path):
    monkeypatch.chdir(dummy_dist)
    bdist_wheel_cmd(bdist_dir=str(tmp_path), build_number="2").run()
    with ZipFile("dist/dummy_dist-1.0-2-py3-none-any.whl") as wf:
        filenames = set(wf.namelist())
        assert "dummy_dist-1.0.dist-info/RECORD" in filenames
        assert "dummy_dist-1.0.dist-info/METADATA" in filenames


def test_universal_deprecated(dummy_dist, monkeypatch, tmp_path):
    monkeypatch.chdir(dummy_dist)
    with pytest.warns(SetuptoolsDeprecationWarning, match=".*universal is deprecated"):
        bdist_wheel_cmd(bdist_dir=str(tmp_path), universal=True).run()

    # For now we still respect the option
    assert os.path.exists("dist/dummy_dist-1.0-py2.py3-none-any.whl")


EXTENSION_EXAMPLE = """\
#include <Python.h>

static PyMethodDef methods[] = {
  { NULL, NULL, 0, NULL }
};

static struct PyModuleDef module_def = {
  PyModuleDef_HEAD_INIT,
  "extension",
  "Dummy extension module",
  -1,
  methods
};

PyMODINIT_FUNC PyInit_extension(void) {
  return PyModule_Create(&module_def);
}
"""
EXTENSION_SETUPPY = """\
from __future__ import annotations

from setuptools import Extension, setup

setup(
    name="extension.dist",
    version="0.1",
    description="A testing distribution \N{SNOWMAN}",
    ext_modules=[Extension(name="extension", sources=["extension.c"])],
)
"""


@pytest.mark.filterwarnings(
    "once:Config variable '.*' is unset.*, Python ABI tag may be incorrect"
)
def test_limited_abi(monkeypatch, tmp_path, tmp_path_factory):
    """Test that building a binary wheel with the limited ABI works."""
    source_dir = tmp_path_factory.mktemp("extension_dist")
    (source_dir / "setup.py").write_text(EXTENSION_SETUPPY, encoding="utf-8")
    (source_dir / "extension.c").write_text(EXTENSION_EXAMPLE, encoding="utf-8")
    build_dir = tmp_path.joinpath("build")
    dist_dir = tmp_path.joinpath("dist")
    monkeypatch.chdir(source_dir)
```
