"""
Typed data-service client facades.
"""

from __future__ import annotations

import json
from typing import Any, Optional

import httpx


class HTTPDatasetClient:
    """Simple HTTP client for JSON dataset APIs."""

    def __init__(self, base_url: str, *, timeout_seconds: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout_seconds)

    def fetch_json(self, path: str, *, params: Optional[dict[str, Any]] = None) -> Any:
        response = self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    def post_json(self, path: str, payload: dict[str, Any]) -> Any:
        response = self._client.post(path, json=payload)
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self._client.close()


class MinioObjectStoreClient:
    """Optional MinIO JSON object facade with graceful dependency handling."""

    def __init__(
        self,
        endpoint: str,
        *,
        access_key: str,
        secret_key: str,
        secure: bool = False,
    ) -> None:
        try:
            from minio import Minio
        except Exception as exc:
            raise RuntimeError(
                "minio package is required for MinioObjectStoreClient"
            ) from exc

        self._client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def put_json(self, bucket: str, key: str, payload: dict[str, Any]) -> None:
        raw = json.dumps(payload).encode("utf-8")
        from io import BytesIO

        self._client.put_object(
            bucket_name=bucket,
            object_name=key,
            data=BytesIO(raw),
            length=len(raw),
            content_type="application/json",
        )

    def get_json(self, bucket: str, key: str) -> dict[str, Any]:
        response = self._client.get_object(bucket, key)
        try:
            return json.loads(response.read().decode("utf-8"))
        finally:
            response.close()
            response.release_conn()

