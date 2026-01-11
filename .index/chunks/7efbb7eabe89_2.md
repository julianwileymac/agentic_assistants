# Chunk: 7efbb7eabe89_2

- source: `.venv-lab/Lib/site-packages/jupyterlab_server/licenses_handler.py`
- lines: 146-228
- chunk: 3/4

```
 [
                    "## "
                    + (
                        "\t".join(
                            [
                                f"""**{name}**""".ljust(longest_name),
                                f"""`{version_info}`""".ljust(20),
                                license_id,
                            ]
                        )
                    )
                ]

                if full_text:
                    if not extracted_text:
                        lines += ["", "> No license text available", ""]
                    else:
                        lines += ["", "", "<pre/>", extracted_text, "</pre>", ""]
        return "\n".join(lines)

    def license_bundle(self, path: Path, bundle: str | None) -> dict[str, Any]:
        """Return the content of a packages's license bundles"""
        bundle_json: dict = {"packages": []}
        checked_paths = []

        for license_file in self.third_party_licenses_files:
            licenses_path = path / license_file
            self.log.debug("Loading licenses from %s", licenses_path)
            if not licenses_path.exists():
                checked_paths += [licenses_path]
                continue

            try:
                file_json = json.loads(licenses_path.read_text(encoding="utf-8"))
            except Exception as err:
                self.log.warning(
                    "Failed to open third-party licenses for %s: %s\n%s",
                    bundle,
                    licenses_path,
                    err,
                )
                continue

            try:
                bundle_json["packages"].extend(file_json["packages"])
            except Exception as err:
                self.log.warning(
                    "Failed to find packages for %s: %s\n%s",
                    bundle,
                    licenses_path,
                    err,
                )
                continue

        if not bundle_json["packages"]:
            self.log.warning("Third-party licenses not found for %s: %s", bundle, checked_paths)

        return bundle_json

    def app_static_info(self) -> tuple[Path | None, str | None]:
        """get the static directory for this app

        This will usually be in `static_dir`, but may also appear in the
        parent of `static_dir`.
        """
        if TYPE_CHECKING:
            from .app import LabServerApp

            assert isinstance(self.parent, LabServerApp)
        path = Path(self.parent.static_dir)
        package_json = path / "package.json"
        if not package_json.exists():
            parent_package_json = path.parent / "package.json"
            if parent_package_json.exists():
                package_json = parent_package_json
            else:
                return None, None
        name = json.loads(package_json.read_text(encoding="utf-8"))["name"]
        return path, name

    def bundles(self, bundles_pattern: str = ".*") -> dict[str, Any]:
        """Read all of the licenses
```
