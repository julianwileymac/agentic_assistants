# Chunk: b9fcb5d33eb1_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/itsdangerous.pyi`
- lines: 1-77
- chunk: 1/4

```
from datetime import datetime
from typing import IO, Any, Callable, Generator, Mapping, MutableMapping, Optional, Text, Tuple, Union

_serializer = Any  # must be an object that has "dumps" and "loads" attributes (e.g. the json module)

def want_bytes(s: Union[Text, bytes], encoding: Text = ..., errors: Text = ...) -> bytes: ...

class BadData(Exception):
    message: str
    def __init__(self, message: str) -> None: ...

class BadPayload(BadData):
    original_error: Optional[Exception]
    def __init__(self, message: str, original_error: Optional[Exception] = ...) -> None: ...

class BadSignature(BadData):
    payload: Optional[Any]
    def __init__(self, message: str, payload: Optional[Any] = ...) -> None: ...

class BadTimeSignature(BadSignature):
    date_signed: Optional[int]
    def __init__(self, message: str, payload: Optional[Any] = ..., date_signed: Optional[int] = ...) -> None: ...

class BadHeader(BadSignature):
    header: Any
    original_error: Any
    def __init__(
        self, message: str, payload: Optional[Any] = ..., header: Optional[Any] = ..., original_error: Optional[Any] = ...
    ) -> None: ...

class SignatureExpired(BadTimeSignature): ...

def base64_encode(string: Union[Text, bytes]) -> bytes: ...
def base64_decode(string: Union[Text, bytes]) -> bytes: ...

class SigningAlgorithm(object):
    def get_signature(self, key: bytes, value: bytes) -> bytes: ...
    def verify_signature(self, key: bytes, value: bytes, sig: bytes) -> bool: ...

class NoneAlgorithm(SigningAlgorithm):
    def get_signature(self, key: bytes, value: bytes) -> bytes: ...

class HMACAlgorithm(SigningAlgorithm):
    default_digest_method: Callable[..., Any]
    digest_method: Callable[..., Any]
    def __init__(self, digest_method: Optional[Callable[..., Any]] = ...) -> None: ...
    def get_signature(self, key: bytes, value: bytes) -> bytes: ...

class Signer(object):
    default_digest_method: Callable[..., Any] = ...
    default_key_derivation: str = ...

    secret_key: bytes
    sep: bytes
    salt: Union[Text, bytes]
    key_derivation: str
    digest_method: Callable[..., Any]
    algorithm: SigningAlgorithm
    def __init__(
        self,
        secret_key: Union[Text, bytes],
        salt: Optional[Union[Text, bytes]] = ...,
        sep: Optional[Union[Text, bytes]] = ...,
        key_derivation: Optional[str] = ...,
        digest_method: Optional[Callable[..., Any]] = ...,
        algorithm: Optional[SigningAlgorithm] = ...,
    ) -> None: ...
    def derive_key(self) -> bytes: ...
    def get_signature(self, value: Union[Text, bytes]) -> bytes: ...
    def sign(self, value: Union[Text, bytes]) -> bytes: ...
    def verify_signature(self, value: bytes, sig: Union[Text, bytes]) -> bool: ...
    def unsign(self, signed_value: Union[Text, bytes]) -> bytes: ...
    def validate(self, signed_value: Union[Text, bytes]) -> bool: ...

class TimestampSigner(Signer):
    def get_timestamp(self) -> int: ...
```
