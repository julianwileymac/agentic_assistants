# Chunk: a64afdbfb071_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/boto/s3/connection.pyi`
- lines: 1-92
- chunk: 1/2

```
from typing import Any, Dict, Optional, Text, Type

from boto.connection import AWSAuthConnection
from boto.exception import BotoClientError

from .bucket import Bucket

def check_lowercase_bucketname(n): ...
def assert_case_insensitive(f): ...

class _CallingFormat:
    def get_bucket_server(self, server, bucket): ...
    def build_url_base(self, connection, protocol, server, bucket, key: str = ...): ...
    def build_host(self, server, bucket): ...
    def build_auth_path(self, bucket, key: str = ...): ...
    def build_path_base(self, bucket, key: str = ...): ...

class SubdomainCallingFormat(_CallingFormat):
    def get_bucket_server(self, server, bucket): ...

class VHostCallingFormat(_CallingFormat):
    def get_bucket_server(self, server, bucket): ...

class OrdinaryCallingFormat(_CallingFormat):
    def get_bucket_server(self, server, bucket): ...
    def build_path_base(self, bucket, key: str = ...): ...

class ProtocolIndependentOrdinaryCallingFormat(OrdinaryCallingFormat):
    def build_url_base(self, connection, protocol, server, bucket, key: str = ...): ...

class Location:
    DEFAULT: str
    EU: str
    EUCentral1: str
    USWest: str
    USWest2: str
    SAEast: str
    APNortheast: str
    APSoutheast: str
    APSoutheast2: str
    CNNorth1: str

class NoHostProvided: ...
class HostRequiredError(BotoClientError): ...

class S3Connection(AWSAuthConnection):
    DefaultHost: Any
    DefaultCallingFormat: Any
    QueryString: str
    calling_format: Any
    bucket_class: Type[Bucket]
    anon: Any
    def __init__(
        self,
        aws_access_key_id: Optional[Any] = ...,
        aws_secret_access_key: Optional[Any] = ...,
        is_secure: bool = ...,
        port: Optional[Any] = ...,
        proxy: Optional[Any] = ...,
        proxy_port: Optional[Any] = ...,
        proxy_user: Optional[Any] = ...,
        proxy_pass: Optional[Any] = ...,
        host: Any = ...,
        debug: int = ...,
        https_connection_factory: Optional[Any] = ...,
        calling_format: Any = ...,
        path: str = ...,
        provider: str = ...,
        bucket_class: Type[Bucket] = ...,
        security_token: Optional[Any] = ...,
        suppress_consec_slashes: bool = ...,
        anon: bool = ...,
        validate_certs: Optional[Any] = ...,
        profile_name: Optional[Any] = ...,
    ) -> None: ...
    def __iter__(self): ...
    def __contains__(self, bucket_name): ...
    def set_bucket_class(self, bucket_class: Type[Bucket]) -> None: ...
    def build_post_policy(self, expiration_time, conditions): ...
    def build_post_form_args(
        self,
        bucket_name,
        key,
        expires_in: int = ...,
        acl: Optional[Any] = ...,
        success_action_redirect: Optional[Any] = ...,
        max_content_length: Optional[Any] = ...,
        http_method: str = ...,
        fields: Optional[Any] = ...,
        conditions: Optional[Any] = ...,
        storage_class: str = ...,
```
