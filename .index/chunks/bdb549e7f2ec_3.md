# Chunk: bdb549e7f2ec_3

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_core_metadata.py`
- lines: 275-365
- chunk: 4/8

```
ge_dicts(attrs, {'author': '鉄沢寛'})),
        ('Maintainer unicode', merge_dicts(attrs, {'maintainer': 'Jan Łukasiewicz'})),
    ]


@pytest.mark.parametrize(("name", "attrs"), __maintainer_test_cases())
def test_maintainer_author(name, attrs, tmpdir):
    tested_keys = {
        'author': 'Author',
        'author_email': 'Author-email',
        'maintainer': 'Maintainer',
        'maintainer_email': 'Maintainer-email',
    }

    # Generate a PKG-INFO file
    dist = Distribution(attrs)
    fn = tmpdir.mkdir('pkg_info')
    fn_s = str(fn)

    dist.metadata.write_pkg_info(fn_s)

    with open(str(fn.join('PKG-INFO')), 'r', encoding='utf-8') as f:
        pkg_info = f.read()

    assert _valid_metadata(pkg_info)

    # Drop blank lines and strip lines from default description
    raw_pkg_lines = pkg_info.splitlines()
    pkg_lines = list(filter(None, raw_pkg_lines[:-2]))

    pkg_lines_set = set(pkg_lines)

    # Duplicate lines should not be generated
    assert len(pkg_lines) == len(pkg_lines_set)

    for fkey, dkey in tested_keys.items():
        val = attrs.get(dkey, None)
        if val is None:
            for line in pkg_lines:
                assert not line.startswith(fkey + ':')
        else:
            line = f'{fkey}: {val}'
            assert line in pkg_lines_set


class TestParityWithMetadataFromPyPaWheel:
    def base_example(self):
        attrs = dict(
            **EXAMPLE_BASE_INFO,
            # Example with complex requirement definition
            python_requires=">=3.8",
            install_requires="""
            packaging==23.2
            more-itertools==8.8.0; extra == "other"
            jaraco.text==3.7.0
            importlib-resources==5.10.2; python_version<"3.8"
            importlib-metadata==6.0.0 ; python_version<"3.8"
            colorama>=0.4.4; sys_platform == "win32"
            """,
            extras_require={
                "testing": """
                    pytest >= 6
                    pytest-checkdocs >= 2.4
                    tomli ; \\
                            # Using stdlib when possible
                            python_version < "3.11"
                    ini2toml[lite]>=0.9
                    """,
                "other": [],
            },
        )
        # Generate a PKG-INFO file using setuptools
        return Distribution(attrs)

    def test_requires_dist(self, tmp_path):
        dist = self.base_example()
        pkg_info = _get_pkginfo(dist)
        assert _valid_metadata(pkg_info)

        # Ensure Requires-Dist is present
        expected = [
            'Metadata-Version:',
            'Requires-Python: >=3.8',
            'Provides-Extra: other',
            'Provides-Extra: testing',
            'Requires-Dist: tomli; python_version < "3.11" and extra == "testing"',
            'Requires-Dist: more-itertools==8.8.0; extra == "other"',
            'Requires-Dist: ini2toml[lite]>=0.9; extra == "testing"',
        ]
        for line in expected:
```
