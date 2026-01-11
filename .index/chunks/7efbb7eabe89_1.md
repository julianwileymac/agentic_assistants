# Chunk: 7efbb7eabe89_1

- source: `.venv-lab/Lib/site-packages/jupyterlab_server/licenses_handler.py`
- lines: 79-154
- chunk: 2/4

```
l_text=full_text,
            )
        )

    def report(self, report_format: str, bundles_pattern: str, full_text: bool) -> tuple[str, str]:
        """create a human- or machine-readable report"""
        bundles = self.bundles(bundles_pattern=bundles_pattern)
        if report_format == "json":
            return self.report_json(bundles), "application/json"
        if report_format == "csv":
            return self.report_csv(bundles), "text/csv"
        if report_format == "markdown":
            return (
                self.report_markdown(bundles, full_text=full_text),
                "text/markdown",
            )

        msg = f"Unsupported report format {report_format}."
        raise ValueError(msg)

    def report_json(self, bundles: dict[str, Any]) -> str:
        """create a JSON report
        TODO: SPDX
        """
        return json.dumps({"bundles": bundles}, indent=2, sort_keys=True)

    def report_csv(self, bundles: dict[str, Any]) -> str:
        """create a CSV report"""
        outfile = io.StringIO()
        fieldnames = ["name", "versionInfo", "licenseId", "extractedText"]
        writer = csv.DictWriter(outfile, fieldnames=["bundle", *fieldnames])
        writer.writeheader()
        for bundle_name, bundle in bundles.items():
            for package in bundle["packages"]:
                writer.writerow(
                    {
                        "bundle": bundle_name,
                        **{field: package.get(field, "") for field in fieldnames},
                    }
                )
        return outfile.getvalue()

    def report_markdown(self, bundles: dict[str, Any], full_text: bool = True) -> str:
        """create a markdown report"""
        lines = []
        library_names = [
            len(package.get("name", UNKNOWN_PACKAGE_NAME))
            for bundle_name, bundle in bundles.items()
            for package in bundle.get("packages", [])
        ]
        longest_name = max(library_names) if library_names else 1

        for bundle_name, bundle in bundles.items():
            # TODO: parametrize template
            lines += [f"# {bundle_name}", ""]

            packages = bundle.get("packages", [])
            if not packages:
                lines += ["> No licenses found", ""]
                continue

            for package in packages:
                name = package.get("name", UNKNOWN_PACKAGE_NAME).strip()
                version_info = package.get("versionInfo", UNKNOWN_PACKAGE_NAME).strip()
                license_id = package.get("licenseId", UNKNOWN_PACKAGE_NAME).strip()
                extracted_text = package.get("extractedText", "")

                lines += [
                    "## "
                    + (
                        "\t".join(
                            [
                                f"""**{name}**""".ljust(longest_name),
                                f"""`{version_info}`""".ljust(20),
                                license_id,
```
