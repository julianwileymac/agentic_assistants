# Chunk: bdb549e7f2ec_5

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_core_metadata.py`
- lines: 416-496
- chunk: 6/8

```
_roundtrip_message(pkg_info)


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
                               description
            description = Short description
            keywords = one, two
            platforms = abcd
            [options]
            install_requires = requests
            """
        ),
        "pyproject.toml": cleandoc(
            """
            [project]
            name = "package"
            version = "0.0.1"
            authors = [
              {name = "Foo Bar", email = "foo@bar.net"}
            ]
            description = "Short description"
            readme = {text = "Long\\ndescription", content-type = "text/plain"}
            keywords = ["one", "two"]
            dependencies = ["requests"]
            license = "AGPL-3.0-or-later"
            [tool.setuptools]
            provides = ["abcd"]
            obsoletes = ["abcd"]
            """
        ),
    }

    @pytest.mark.parametrize("file", STATIC_CONFIG.keys())
    def test_static_config_has_no_dynamic(self, file, tmpdir_cwd):
        Path(file).write_text(self.STATIC_CONFIG[file], encoding="utf-8")
        metadata = _get_metadata()
        assert metadata.get_all("Dynamic") is None
        assert metadata.get_all("dynamic") is None

    @pytest.mark.parametrize("file", STATIC_CONFIG.keys())
    @pytest.mark.parametrize(
        "fields",
        [
            # Single dynamic field
            {"requires-python": ("python_requires", ">=3.12")},
            {"author-email": ("author_email", "snoopy@peanuts.com")},
            {"keywords": ("keywords", ["hello", "world"])},
            {"platform": ("platforms", ["abcd"])},
            # Multiple dynamic fields
            {
                "summary": ("description", "hello world"),
                "description": ("long_description", "bla bla bla bla"),
                "requires-dist": ("install_requires", ["hello-world"]),
            },
        ],
    )
    def test_modified_fields_marked_as_dynamic(self, file, fields, tmpdir_cwd):
        # We start with a static config
        Path(file).write_text(self.STATIC_CONFIG[file], encoding="utf-8")
        dist = _makedist()

        # ... but then we simulate the effects of a plugin modifying the distribution
        for attr, value in fields.values():
            # `dist` and `dist.metadata` are complicated...
            # Some attributes work when set on `dist`, others on `dist.metadata`...
            # Here we set in both just in case (this also avoids calling `_finalize_*`)
            setattr(dist, attr, value)
            setattr(dist.metadata, attr, value)

        # Then we should be able to list the modified fields as Dynamic
        metadata = _get_metadata(dist)
```
