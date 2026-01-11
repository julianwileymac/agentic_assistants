# Chunk: 0e7deda551fc_4

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/contents/handlers.py`
- lines: 300-388
- chunk: 5/6

```
,
          create a new empty notebook.
        """
        model = self.get_json_body()
        cm = self.contents_manager

        if model:
            if model.get("copy_from"):
                raise web.HTTPError(400, "Cannot copy with PUT, only POST")
            if not cm.allow_hidden and (
                (model.get("path") and await ensure_async(cm.is_hidden(model.get("path"))))
                or await ensure_async(cm.is_hidden(path))
            ):
                raise web.HTTPError(400, f"Cannot create file or directory {path!r}")

            exists = await ensure_async(self.contents_manager.file_exists(path))
            if model.get("type", "") not in {None, "", "directory", "file", "notebook"}:
                # fall back to file if unknown type
                model["type"] = "file"
            if exists:
                await self._save(model, path)
            else:
                await self._upload(model, path)
        else:
            await self._new_untitled(path)

    @web.authenticated
    @authorized
    async def delete(self, path=""):
        """delete a file in the given path"""
        cm = self.contents_manager

        if not cm.allow_hidden and await ensure_async(cm.is_hidden(path)):
            raise web.HTTPError(400, f"Cannot delete file or directory {path!r}")

        self.log.warning("delete %s", path)
        await ensure_async(cm.delete(path))
        self.set_status(204)
        self.finish()


class CheckpointsHandler(ContentsAPIHandler):
    """A checkpoints API handler."""

    @web.authenticated
    @authorized
    async def get(self, path=""):
        """get lists checkpoints for a file"""
        cm = self.contents_manager
        checkpoints = await ensure_async(cm.list_checkpoints(path))
        data = json.dumps(checkpoints, default=json_default)
        self.finish(data)

    @web.authenticated
    @authorized
    async def post(self, path=""):
        """post creates a new checkpoint"""
        cm = self.contents_manager
        checkpoint = await ensure_async(cm.create_checkpoint(path))
        data = json.dumps(checkpoint, default=json_default)
        location = url_path_join(
            self.base_url,
            "api/contents",
            url_escape(path),
            "checkpoints",
            url_escape(checkpoint["id"]),
        )
        self.set_header("Location", location)
        self.set_status(201)
        self.finish(data)


class ModifyCheckpointsHandler(ContentsAPIHandler):
    """A checkpoints modification handler."""

    @web.authenticated
    @authorized
    async def post(self, path, checkpoint_id):
        """post restores a file from a checkpoint"""
        cm = self.contents_manager
        await ensure_async(cm.restore_checkpoint(checkpoint_id, path))
        self.set_status(204)
        self.finish()

    @web.authenticated
    @authorized
    async def delete(self, path, checkpoint_id):
        """delete clears a checkpoint for a given file"""
```
