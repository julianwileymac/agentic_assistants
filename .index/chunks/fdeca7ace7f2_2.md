# Chunk: fdeca7ace7f2_2

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_distutils_adoption.py`
- lines: 182-199
- chunk: 3/3

```
     # But that's a deprecated use-case we don't mind not fully supporting in newer code
        pytest.param(
            "stdlib", "setuptools._distutils", marks=skip_without_stdlib_distutils
        ),
    ],
)
def test_consistent_error_from_modified_py(distutils_version, imported_module, venv):
    env = dict(SETUPTOOLS_USE_DISTUTILS=distutils_version)
    cmd = [
        'python',
        '-c',
        ENSURE_CONSISTENT_ERROR_FROM_MODIFIED_PY.format(
            imported_module=imported_module
        ),
    ]
    output = venv.run(cmd, env=win_sr(env), **_TEXT_KWARGS).strip()
    assert output == "success"
```
