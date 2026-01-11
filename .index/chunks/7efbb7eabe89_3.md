# Chunk: 7efbb7eabe89_3

- source: `.venv-lab/Lib/site-packages/jupyterlab_server/licenses_handler.py`
- lines: 220-290
- chunk: 4/4

```
    package_json = parent_package_json
            else:
                return None, None
        name = json.loads(package_json.read_text(encoding="utf-8"))["name"]
        return path, name

    def bundles(self, bundles_pattern: str = ".*") -> dict[str, Any]:
        """Read all of the licenses
        TODO: schema
        """
        bundles = {
            name: self.license_bundle(Path(ext["ext_path"]), name)
            for name, ext in self.federated_extensions.items()
            if re.match(bundles_pattern, name)
        }

        app_path, app_name = self.app_static_info()
        if app_path is not None:
            assert app_name is not None
            if re.match(bundles_pattern, app_name):
                bundles[app_name] = self.license_bundle(app_path, app_name)

        if not bundles:
            self.log.warning("No license bundles found at all")

        return bundles


class LicensesHandler(APIHandler):
    """A handler for serving licenses used by the application"""

    def initialize(self, manager: LicensesManager) -> None:
        """Initialize the handler."""
        super().initialize()
        self.manager = manager

    @web.authenticated
    async def get(self, _args: Any) -> None:
        """Return all the frontend licenses"""
        full_text = bool(json.loads(self.get_argument("full_text", "true")))
        report_format = self.get_argument("format", "json")
        bundles_pattern = self.get_argument("bundles", ".*")
        download = bool(json.loads(self.get_argument("download", "0")))

        report, mime = await self.manager.report_async(
            report_format=report_format,
            bundles_pattern=bundles_pattern,
            full_text=full_text,
        )

        if TYPE_CHECKING:
            from .app import LabServerApp

            assert isinstance(self.manager.parent, LabServerApp)

        if download:
            filename = "{}-licenses{}".format(
                self.manager.parent.app_name.lower(), mimetypes.guess_extension(mime)
            )
            self.set_attachment_header(filename)
        self.write(report)
        await self.finish(_mime_type=mime)

    async def finish(  # type:ignore[override]
        self, _mime_type: str, *args: Any, **kwargs: Any
    ) -> Any:
        """Overload the regular finish, which (sensibly) always sets JSON"""
        self.update_api_activity()
        self.set_header("Content-Type", _mime_type)
        return await super(APIHandler, self).finish(*args, **kwargs)
```
