"""
MinIO/S3 storage integration for Kubernetes deployments.

Provides object storage operations for artifacts, models, and
distributed state management.
"""

import io
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Optional, Union

from agentic_assistants.config import AgenticConfig

logger = logging.getLogger(__name__)


class MinIOStorage:
    """
    MinIO/S3-compatible object storage client.
    
    Provides operations for storing and retrieving artifacts,
    model files, and distributed state.
    
    Example:
        >>> storage = MinIOStorage()
        >>> await storage.upload_file("my-bucket", "path/to/file.txt", local_path)
        >>> data = await storage.download_file("my-bucket", "path/to/file.txt")
    """

    def __init__(self, config: Optional[AgenticConfig] = None):
        """
        Initialize MinIO storage client.
        
        Args:
            config: Agentic configuration instance
        """
        self.config = config or AgenticConfig()
        self._client = None
        self._initialized = False
        self._minio_available = False
        
        # Check if minio library is available
        try:
            from minio import Minio
            self._minio_available = True
        except ImportError:
            logger.warning("minio library not installed. MinIO features disabled.")

    def _initialize(self) -> bool:
        """Initialize MinIO client."""
        if self._initialized:
            return self._minio_available and self._client is not None
        
        if not self._minio_available:
            self._initialized = True
            return False
        
        minio_config = self.config.minio
        if not minio_config.enabled:
            logger.info("MinIO storage is disabled in configuration")
            self._initialized = True
            return False
        
        try:
            from minio import Minio
            
            # Use external endpoint if available, otherwise internal
            endpoint = minio_config.external_endpoint or minio_config.endpoint
            
            self._client = Minio(
                endpoint,
                access_key=minio_config.access_key,
                secret_key=minio_config.secret_key,
                secure=minio_config.secure,
                region=minio_config.region,
            )
            
            self._initialized = True
            logger.info(f"MinIO client initialized: {endpoint}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            self._initialized = True
            return False

    @property
    def is_available(self) -> bool:
        """Check if MinIO client is available."""
        self._initialize()
        return self._client is not None

    @property
    def client(self):
        """Get the MinIO client instance."""
        self._initialize()
        return self._client

    async def ensure_bucket(self, bucket_name: str) -> bool:
        """
        Ensure a bucket exists, creating it if necessary.
        
        Args:
            bucket_name: Name of the bucket
            
        Returns:
            True if bucket exists or was created
        """
        if not self._initialize():
            return False
        
        try:
            if not self._client.bucket_exists(bucket_name):
                self._client.make_bucket(bucket_name)
                logger.info(f"Created bucket: {bucket_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to ensure bucket {bucket_name}: {e}")
            return False

    async def list_buckets(self) -> list[str]:
        """List all buckets."""
        if not self._initialize():
            return []
        
        try:
            buckets = self._client.list_buckets()
            return [b.name for b in buckets]
        except Exception as e:
            logger.error(f"Failed to list buckets: {e}")
            return []

    async def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        file_path: Union[str, Path],
        content_type: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> bool:
        """
        Upload a file to MinIO.
        
        Args:
            bucket_name: Target bucket
            object_name: Object path in bucket
            file_path: Local file path
            content_type: MIME type (auto-detected if None)
            metadata: Additional metadata
            
        Returns:
            True if upload successful
        """
        if not self._initialize():
            return False
        
        try:
            await self.ensure_bucket(bucket_name)
            
            self._client.fput_object(
                bucket_name,
                object_name,
                str(file_path),
                content_type=content_type,
                metadata=metadata,
            )
            logger.info(f"Uploaded {file_path} to {bucket_name}/{object_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return False

    async def upload_data(
        self,
        bucket_name: str,
        object_name: str,
        data: Union[bytes, str, BinaryIO],
        content_type: str = "application/octet-stream",
        metadata: Optional[dict[str, str]] = None,
    ) -> bool:
        """
        Upload data directly to MinIO.
        
        Args:
            bucket_name: Target bucket
            object_name: Object path in bucket
            data: Data to upload (bytes, string, or file-like object)
            content_type: MIME type
            metadata: Additional metadata
            
        Returns:
            True if upload successful
        """
        if not self._initialize():
            return False
        
        try:
            await self.ensure_bucket(bucket_name)
            
            # Convert to bytes if string
            if isinstance(data, str):
                data = data.encode("utf-8")
                content_type = "text/plain"
            
            # Create BytesIO if bytes
            if isinstance(data, bytes):
                data_stream = io.BytesIO(data)
                length = len(data)
            else:
                # Assume file-like object
                data_stream = data
                data_stream.seek(0, 2)  # Seek to end
                length = data_stream.tell()
                data_stream.seek(0)  # Seek back to start
            
            self._client.put_object(
                bucket_name,
                object_name,
                data_stream,
                length,
                content_type=content_type,
                metadata=metadata,
            )
            logger.info(f"Uploaded data to {bucket_name}/{object_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload data: {e}")
            return False

    async def download_file(
        self,
        bucket_name: str,
        object_name: str,
        file_path: Union[str, Path],
    ) -> bool:
        """
        Download a file from MinIO.
        
        Args:
            bucket_name: Source bucket
            object_name: Object path in bucket
            file_path: Local destination path
            
        Returns:
            True if download successful
        """
        if not self._initialize():
            return False
        
        try:
            self._client.fget_object(
                bucket_name,
                object_name,
                str(file_path),
            )
            logger.info(f"Downloaded {bucket_name}/{object_name} to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            return False

    async def download_data(
        self,
        bucket_name: str,
        object_name: str,
    ) -> Optional[bytes]:
        """
        Download data from MinIO.
        
        Args:
            bucket_name: Source bucket
            object_name: Object path in bucket
            
        Returns:
            File contents as bytes, or None if failed
        """
        if not self._initialize():
            return None
        
        try:
            response = self._client.get_object(bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
            
        except Exception as e:
            logger.error(f"Failed to download data: {e}")
            return None

    async def delete_object(
        self,
        bucket_name: str,
        object_name: str,
    ) -> bool:
        """Delete an object from MinIO."""
        if not self._initialize():
            return False
        
        try:
            self._client.remove_object(bucket_name, object_name)
            logger.info(f"Deleted {bucket_name}/{object_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete object: {e}")
            return False

    async def list_objects(
        self,
        bucket_name: str,
        prefix: Optional[str] = None,
        recursive: bool = False,
    ) -> list[dict]:
        """
        List objects in a bucket.
        
        Args:
            bucket_name: Bucket to list
            prefix: Filter by prefix
            recursive: Include objects in subdirectories
            
        Returns:
            List of object info dicts
        """
        if not self._initialize():
            return []
        
        try:
            objects = self._client.list_objects(
                bucket_name,
                prefix=prefix,
                recursive=recursive,
            )
            
            result = []
            for obj in objects:
                result.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
                    "etag": obj.etag,
                    "is_dir": obj.is_dir,
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to list objects: {e}")
            return []

    async def get_object_info(
        self,
        bucket_name: str,
        object_name: str,
    ) -> Optional[dict]:
        """Get metadata for an object."""
        if not self._initialize():
            return None
        
        try:
            stat = self._client.stat_object(bucket_name, object_name)
            return {
                "name": stat.object_name,
                "size": stat.size,
                "last_modified": stat.last_modified.isoformat() if stat.last_modified else None,
                "etag": stat.etag,
                "content_type": stat.content_type,
                "metadata": dict(stat.metadata) if stat.metadata else {},
            }
        except Exception as e:
            logger.error(f"Failed to get object info: {e}")
            return None

    async def upload_json(
        self,
        bucket_name: str,
        object_name: str,
        data: Any,
        metadata: Optional[dict[str, str]] = None,
    ) -> bool:
        """Upload JSON data to MinIO."""
        json_str = json.dumps(data, default=str)
        return await self.upload_data(
            bucket_name,
            object_name,
            json_str,
            content_type="application/json",
            metadata=metadata,
        )

    async def download_json(
        self,
        bucket_name: str,
        object_name: str,
    ) -> Optional[Any]:
        """Download and parse JSON data from MinIO."""
        data = await self.download_data(bucket_name, object_name)
        if data is None:
            return None
        
        try:
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return None

    async def copy_object(
        self,
        source_bucket: str,
        source_object: str,
        dest_bucket: str,
        dest_object: str,
    ) -> bool:
        """Copy an object within MinIO."""
        if not self._initialize():
            return False
        
        try:
            from minio.commonconfig import CopySource
            
            await self.ensure_bucket(dest_bucket)
            
            self._client.copy_object(
                dest_bucket,
                dest_object,
                CopySource(source_bucket, source_object),
            )
            logger.info(f"Copied {source_bucket}/{source_object} to {dest_bucket}/{dest_object}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy object: {e}")
            return False

    async def get_presigned_url(
        self,
        bucket_name: str,
        object_name: str,
        expires_hours: int = 1,
    ) -> Optional[str]:
        """
        Generate a presigned URL for an object.
        
        Args:
            bucket_name: Bucket name
            object_name: Object path
            expires_hours: URL expiration time in hours
            
        Returns:
            Presigned URL or None if failed
        """
        if not self._initialize():
            return None
        
        try:
            from datetime import timedelta
            
            url = self._client.presigned_get_object(
                bucket_name,
                object_name,
                expires=timedelta(hours=expires_hours),
            )
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None

    async def test_connection(self) -> dict:
        """
        Test the MinIO connection.
        
        Returns:
            Dict with connection status and details
        """
        if not self._minio_available:
            return {
                "connected": False,
                "error": "minio library not installed",
            }
        
        if not self.config.minio.enabled:
            return {
                "connected": False,
                "error": "MinIO storage is disabled",
            }
        
        try:
            self._initialize()
            if not self._client:
                return {
                    "connected": False,
                    "error": "Failed to initialize client",
                }
            
            # Try to list buckets
            buckets = await self.list_buckets()
            
            return {
                "connected": True,
                "endpoint": self.config.minio.external_endpoint or self.config.minio.endpoint,
                "buckets": buckets,
            }
            
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
            }

    # Artifact storage helpers
    
    async def store_artifact(
        self,
        artifact_id: str,
        data: Union[bytes, str, Path],
        artifact_type: str = "generic",
        metadata: Optional[dict[str, str]] = None,
    ) -> bool:
        """
        Store an artifact in the default bucket.
        
        Args:
            artifact_id: Unique artifact identifier
            data: Artifact data (bytes, string, or file path)
            artifact_type: Type of artifact for organization
            metadata: Additional metadata
            
        Returns:
            True if stored successfully
        """
        bucket = self.config.minio.default_bucket
        object_name = f"artifacts/{artifact_type}/{artifact_id}"
        
        meta = metadata or {}
        meta["artifact_type"] = artifact_type
        meta["stored_at"] = datetime.utcnow().isoformat()
        
        if isinstance(data, Path):
            return await self.upload_file(bucket, object_name, data, metadata=meta)
        else:
            return await self.upload_data(bucket, object_name, data, metadata=meta)

    async def retrieve_artifact(
        self,
        artifact_id: str,
        artifact_type: str = "generic",
    ) -> Optional[bytes]:
        """
        Retrieve an artifact from the default bucket.
        
        Args:
            artifact_id: Artifact identifier
            artifact_type: Type of artifact
            
        Returns:
            Artifact data or None if not found
        """
        bucket = self.config.minio.default_bucket
        object_name = f"artifacts/{artifact_type}/{artifact_id}"
        return await self.download_data(bucket, object_name)

    async def list_artifacts(
        self,
        artifact_type: Optional[str] = None,
    ) -> list[dict]:
        """
        List artifacts in the default bucket.
        
        Args:
            artifact_type: Filter by artifact type
            
        Returns:
            List of artifact info dicts
        """
        bucket = self.config.minio.default_bucket
        prefix = f"artifacts/{artifact_type}/" if artifact_type else "artifacts/"
        return await self.list_objects(bucket, prefix=prefix, recursive=True)
