# Chunk: d41d90eff3fc_7

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/contents/fileio.py`
- lines: 539-600
- chunk: 8/8

```
: bool
            [Optional] If True, will return as third argument the raw bytes content

        Returns
        -------
        (content, format, byte_content) It returns the content in the given format
        as well as the raw byte content.
        """
        if not os.path.isfile(os_path):
            raise HTTPError(400, "Cannot read non-file %s" % os_path)

        with self.open(os_path, "rb") as f:
            bcontent = await run_sync(f.read)

        if format == "byte":
            # Not for http response but internal use
            return (bcontent, "byte", bcontent) if raw else (bcontent, "byte")

        if format is None or format == "text":
            # Try to interpret as unicode if format is unknown or if unicode
            # was explicitly requested.
            try:
                return (
                    (bcontent.decode("utf8"), "text", bcontent)
                    if raw
                    else (
                        bcontent.decode("utf8"),
                        "text",
                    )
                )
            except UnicodeError as e:
                if format == "text":
                    raise HTTPError(
                        400,
                        "%s is not UTF-8 encoded" % os_path,
                        reason="bad format",
                    ) from e
        return (
            (encodebytes(bcontent).decode("ascii"), "base64", bcontent)
            if raw
            else (encodebytes(bcontent).decode("ascii"), "base64")
        )

    async def _save_file(self, os_path, content, format):
        """Save content of a generic file."""
        if format not in {"text", "base64"}:
            raise HTTPError(
                400,
                "Must specify format of file contents as 'text' or 'base64'",
            )
        try:
            if format == "text":
                bcontent = content.encode("utf8")
            else:
                b64_bytes = content.encode("ascii")
                bcontent = decodebytes(b64_bytes)
        except Exception as e:
            raise HTTPError(400, f"Encoding error saving {os_path}: {e}") from e

        with self.atomic_writing(os_path, text=False) as f:
            await run_sync(f.write, bcontent)
```
