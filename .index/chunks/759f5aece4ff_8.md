# Chunk: 759f5aece4ff_8

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_bdist_wheel.py`
- lines: 666-709
- chunk: 9/9

```
eypatch, tmp_path):
    # Motivation: https://github.com/pypa/setuptools/issues/4892
    # TODO: Remove this test after deprecation period is over
    files = {
        "LICENSE.txt": "parent license",  # <---- the license files are outside
        "NOTICE.txt": "parent notice",
        "python": {
            "pyproject.toml": cleandoc(
                """
                [project]
                name = "test-proj"
                dynamic = ["version"]      # <---- testing dynamic will not break
                [tool.setuptools.dynamic]
                version.file = "VERSION"
                """
            ),
            "setup.cfg": cleandoc(
                """
                [metadata]
                license_files =
                  ../LICENSE.txt
                  ../NOTICE.txt
                """
            ),
            "VERSION": "42",
        },
    }
    jaraco.path.build(files, prefix=str(tmp_path))
    monkeypatch.chdir(tmp_path / "python")
    msg = "Pattern '../.*.txt' cannot contain '..'"
    with pytest.warns(SetuptoolsDeprecationWarning, match=msg):
        bdist_wheel_cmd().run()
    with ZipFile("dist/test_proj-42-py3-none-any.whl") as wf:
        files_found = set(wf.namelist())
        expected_files = {
            "test_proj-42.dist-info/licenses/LICENSE.txt",
            "test_proj-42.dist-info/licenses/NOTICE.txt",
        }
        assert expected_files <= files_found

        metadata = wf.read("test_proj-42.dist-info/METADATA").decode("utf8")
        assert "License-File: LICENSE.txt" in metadata
        assert "License-File: NOTICE.txt" in metadata
```
