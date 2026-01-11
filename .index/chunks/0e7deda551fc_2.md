# Chunk: 0e7deda551fc_2

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/contents/handlers.py`
- lines: 162-241
- chunk: 3/6

```
require_hash=require_hash,
                    )
                )
            except TypeError:
                # Fallback for ContentsManager not handling the require_hash argument
                # introduced in 2.11
                expect_hash = False
                model = await ensure_async(
                    self.contents_manager.get(
                        path=path,
                        type=type,
                        format=format,
                        content=content,
                    )
                )
            validate_model(model, expect_content=content, expect_hash=expect_hash)
            self._finish_model(model, location=False)
        except web.HTTPError as exc:
            # 404 is okay in this context, catch exception and return 404 code to prevent stack trace on client
            if exc.status_code == HTTPStatus.NOT_FOUND:
                await self._finish_error(
                    HTTPStatus.NOT_FOUND, f"file or directory {path!r} does not exist"
                )
            raise

    @web.authenticated
    @authorized
    async def patch(self, path=""):
        """PATCH renames a file or directory without re-uploading content."""
        cm = self.contents_manager
        model = self.get_json_body()
        if model is None:
            raise web.HTTPError(400, "JSON body missing")

        old_path = model.get("path")
        if (
            old_path
            and not cm.allow_hidden
            and (
                await ensure_async(cm.is_hidden(path)) or await ensure_async(cm.is_hidden(old_path))
            )
        ):
            raise web.HTTPError(400, f"Cannot rename file or directory {path!r}")

        model = await ensure_async(cm.update(model, path))
        validate_model(model)
        self._finish_model(model)

    async def _copy(self, copy_from, copy_to=None):
        """Copy a file, optionally specifying a target directory."""
        self.log.info(
            "Copying %r to %r",
            copy_from,
            copy_to or "",
        )
        model = await ensure_async(self.contents_manager.copy(copy_from, copy_to))
        self.set_status(201)
        validate_model(model)
        self._finish_model(model)

    async def _upload(self, model, path):
        """Handle upload of a new file to path"""
        self.log.info("Uploading file to %s", path)
        model = await ensure_async(self.contents_manager.new(model, path))
        self.set_status(201)
        validate_model(model)
        self._finish_model(model)

    async def _new_untitled(self, path, type="", ext=""):
        """Create a new, empty untitled entity"""
        self.log.info("Creating new %s in %s", type or "file", path)
        model = await ensure_async(
            self.contents_manager.new_untitled(path=path, type=type, ext=ext)
        )
        self.set_status(201)
        validate_model(model)
        self._finish_model(model)

    async def _save(self, model, path):
```
