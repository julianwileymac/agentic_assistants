# Chunk: d41d90eff3fc_6

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/contents/fileio.py`
- lines: 466-548
- chunk: 7/8

```
 dest

        like shutil.copy2, but log errors in copystat
        """
        await async_copy2_safe(src, dest, log=self.log)

    async def _read_notebook(
        self, os_path, as_version=4, capture_validation_error=None, raw: bool = False
    ):
        """Read a notebook from an os path."""
        answer = await self._read_file(os_path, "text", raw)

        try:
            nb = await run_sync(
                partial(
                    nbformat.reads,
                    as_version=as_version,
                    capture_validation_error=capture_validation_error,
                ),
                answer[0],
            )
            return (nb, answer[2]) if raw else nb  # type:ignore[misc]
        except Exception as e:
            e_orig = e

        # If use_atomic_writing is enabled, we'll guess that it was also
        # enabled when this notebook was written and look for a valid
        # atomic intermediate.
        tmp_path = path_to_intermediate(os_path)

        if not self.use_atomic_writing or not os.path.exists(tmp_path):
            raise HTTPError(
                400,
                f"Unreadable Notebook: {os_path} {e_orig!r}",
            )

        # Move the bad file aside, restore the intermediate, and try again.
        invalid_file = path_to_invalid(os_path)
        await async_replace_file(os_path, invalid_file)
        await async_replace_file(tmp_path, os_path)
        answer = await self._read_notebook(
            os_path, as_version, capture_validation_error=capture_validation_error, raw=raw
        )

        return answer

    async def _save_notebook(self, os_path, nb, capture_validation_error=None):
        """Save a notebook to an os_path."""
        with self.atomic_writing(os_path, encoding="utf-8") as f:
            await run_sync(
                partial(
                    nbformat.write,
                    version=nbformat.NO_CONVERT,
                    capture_validation_error=capture_validation_error,
                ),
                nb,
                f,
            )

    async def _read_file(  # type: ignore[override]
        self, os_path: str, format: str | None, raw: bool = False
    ) -> tuple[str | bytes, str] | tuple[str | bytes, str, bytes]:
        """Read a non-notebook file.

        Parameters
        ----------
        os_path: str
            The path to be read.
        format: str
            If 'text', the contents will be decoded as UTF-8.
            If 'base64', the raw bytes contents will be encoded as base64.
            If 'byte', the raw bytes contents will be returned.
            If not specified, try to decode as UTF-8, and fall back to base64
        raw: bool
            [Optional] If True, will return as third argument the raw bytes content

        Returns
        -------
        (content, format, byte_content) It returns the content in the given format
        as well as the raw byte content.
        """
        if not os.path.isfile(os_path):
```
