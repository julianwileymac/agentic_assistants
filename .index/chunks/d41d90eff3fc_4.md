# Chunk: d41d90eff3fc_4

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/contents/fileio.py`
- lines: 313-397
- chunk: 5/8

```
h

    def _read_notebook(
        self, os_path, as_version=4, capture_validation_error=None, raw: bool = False
    ):
        """Read a notebook from an os path."""
        answer = self._read_file(os_path, "text", raw=raw)

        try:
            nb = nbformat.reads(
                answer[0],
                as_version=as_version,
                capture_validation_error=capture_validation_error,
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
        replace_file(os_path, invalid_file)
        replace_file(tmp_path, os_path)
        return self._read_notebook(
            os_path, as_version, capture_validation_error=capture_validation_error, raw=raw
        )

    def _save_notebook(self, os_path, nb, capture_validation_error=None):
        """Save a notebook to an os_path."""
        with self.atomic_writing(os_path, encoding="utf-8") as f:
            nbformat.write(
                nb,
                f,
                version=nbformat.NO_CONVERT,
                capture_validation_error=capture_validation_error,
            )

    def _get_hash(self, byte_content: bytes) -> dict[str, str]:
        """Compute the hash hexdigest for the provided bytes.

        The hash algorithm is provided by the `hash_algorithm` attribute.

        Parameters
        ----------
        byte_content : bytes
            The bytes to hash

        Returns
        -------
        A dictionary to be appended to a model {"hash": str, "hash_algorithm": str}.
        """
        algorithm = self.hash_algorithm
        h = hashlib.new(algorithm)
        h.update(byte_content)
        return {"hash": h.hexdigest(), "hash_algorithm": algorithm}

    def _read_file(
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
```
