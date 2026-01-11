# Chunk: e7beb2ef26c5_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/boto/s3/bucket.pyi`
- lines: 1-82
- chunk: 1/4

```
from typing import Any, Dict, List, Optional, Text, Type

from .bucketlistresultset import BucketListResultSet
from .connection import S3Connection
from .key import Key

class S3WebsiteEndpointTranslate:
    trans_region: Dict[str, str]
    @classmethod
    def translate_region(cls, reg: Text) -> str: ...

S3Permissions: List[str]

class Bucket:
    LoggingGroup: str
    BucketPaymentBody: str
    VersioningBody: str
    VersionRE: str
    MFADeleteRE: str
    name: Text
    connection: S3Connection
    key_class: Type[Key]
    def __init__(
        self, connection: Optional[S3Connection] = ..., name: Optional[Text] = ..., key_class: Type[Key] = ...
    ) -> None: ...
    def __iter__(self): ...
    def __contains__(self, key_name) -> bool: ...
    def startElement(self, name, attrs, connection): ...
    creation_date: Any
    def endElement(self, name, value, connection): ...
    def set_key_class(self, key_class): ...
    def lookup(self, key_name, headers: Optional[Dict[Text, Text]] = ...): ...
    def get_key(
        self,
        key_name,
        headers: Optional[Dict[Text, Text]] = ...,
        version_id: Optional[Any] = ...,
        response_headers: Optional[Dict[Text, Text]] = ...,
        validate: bool = ...,
    ) -> Key: ...
    def list(
        self,
        prefix: Text = ...,
        delimiter: Text = ...,
        marker: Text = ...,
        headers: Optional[Dict[Text, Text]] = ...,
        encoding_type: Optional[Any] = ...,
    ) -> BucketListResultSet: ...
    def list_versions(
        self,
        prefix: str = ...,
        delimiter: str = ...,
        key_marker: str = ...,
        version_id_marker: str = ...,
        headers: Optional[Dict[Text, Text]] = ...,
        encoding_type: Optional[Text] = ...,
    ) -> BucketListResultSet: ...
    def list_multipart_uploads(
        self,
        key_marker: str = ...,
        upload_id_marker: str = ...,
        headers: Optional[Dict[Text, Text]] = ...,
        encoding_type: Optional[Any] = ...,
    ): ...
    def validate_kwarg_names(self, kwargs, names): ...
    def get_all_keys(self, headers: Optional[Dict[Text, Text]] = ..., **params): ...
    def get_all_versions(self, headers: Optional[Dict[Text, Text]] = ..., **params): ...
    def validate_get_all_versions_params(self, params): ...
    def get_all_multipart_uploads(self, headers: Optional[Dict[Text, Text]] = ..., **params): ...
    def new_key(self, key_name: Optional[Any] = ...): ...
    def generate_url(
        self,
        expires_in,
        method: str = ...,
        headers: Optional[Dict[Text, Text]] = ...,
        force_http: bool = ...,
        response_headers: Optional[Dict[Text, Text]] = ...,
        expires_in_absolute: bool = ...,
    ): ...
    def delete_keys(self, keys, quiet: bool = ..., mfa_token: Optional[Any] = ..., headers: Optional[Dict[Text, Text]] = ...): ...
    def delete_key(
```
