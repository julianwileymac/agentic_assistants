# Chunk: bdb549e7f2ec_4

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_core_metadata.py`
- lines: 359-429
- chunk: 5/8

```
         'Provides-Extra: testing',
            'Requires-Dist: tomli; python_version < "3.11" and extra == "testing"',
            'Requires-Dist: more-itertools==8.8.0; extra == "other"',
            'Requires-Dist: ini2toml[lite]>=0.9; extra == "testing"',
        ]
        for line in expected:
            assert line in pkg_info

    HERE = Path(__file__).parent
    EXAMPLES_FILE = HERE / "config/setupcfg_examples.txt"

    @pytest.fixture(params=[None, *urls_from_file(EXAMPLES_FILE)])
    def dist(self, request, monkeypatch, tmp_path):
        """Example of distribution with arbitrary configuration"""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(expand, "read_attr", Mock(return_value="0.42"))
        monkeypatch.setattr(expand, "read_files", Mock(return_value="hello world"))
        monkeypatch.setattr(
            Distribution, "_finalize_license_files", Mock(return_value=None)
        )
        if request.param is None:
            yield self.base_example()
        else:
            # Real-world usage
            config = retrieve_file(request.param)
            yield setupcfg.apply_configuration(Distribution({}), config)

    @pytest.mark.uses_network
    def test_equivalent_output(self, tmp_path, dist):
        """Ensure output from setuptools is equivalent to the one from `pypa/wheel`"""
        # Generate a METADATA file using pypa/wheel for comparison
        wheel_metadata = importlib.import_module("wheel.metadata")
        pkginfo_to_metadata = getattr(wheel_metadata, "pkginfo_to_metadata", None)

        if pkginfo_to_metadata is None:  # pragma: nocover
            pytest.xfail(
                "wheel.metadata.pkginfo_to_metadata is undefined, "
                "(this is likely to be caused by API changes in pypa/wheel"
            )

        # Generate an simplified "egg-info" dir for pypa/wheel to convert
        pkg_info = _get_pkginfo(dist)
        egg_info_dir = tmp_path / "pkg.egg-info"
        egg_info_dir.mkdir(parents=True)
        (egg_info_dir / "PKG-INFO").write_text(pkg_info, encoding="utf-8")
        write_requirements(egg_info(dist), egg_info_dir, egg_info_dir / "requires.txt")

        # Get pypa/wheel generated METADATA but normalize requirements formatting
        metadata_msg = pkginfo_to_metadata(egg_info_dir, egg_info_dir / "PKG-INFO")
        metadata_str = _normalize_metadata(metadata_msg)
        pkg_info_msg = message_from_string(pkg_info)
        pkg_info_str = _normalize_metadata(pkg_info_msg)

        # Compare setuptools PKG-INFO x pypa/wheel METADATA
        assert metadata_str == pkg_info_str

        # Make sure it parses/serializes well in pypa/wheel
        _assert_roundtrip_message(pkg_info)


class TestPEP643:
    STATIC_CONFIG = {
        "setup.cfg": cleandoc(
            """
            [metadata]
            name = package
            version = 0.0.1
            author = Foo Bar
            author_email = foo@bar.net
            long_description = Long
```
