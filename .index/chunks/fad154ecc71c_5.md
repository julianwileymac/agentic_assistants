# Chunk: fad154ecc71c_5

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/urllib/request.pyi`
- lines: 293-342
- chunk: 6/6

```
, errcode: int, errmsg: str, headers: Mapping[str, str], data: Optional[bytes] = ...
    ) -> Optional[Union[_UrlopenRet, addinfourl]]: ...  # undocumented
    def http_error_302(
        self, url: str, fp: IO[str], errcode: int, errmsg: str, headers: Mapping[str, str], data: Optional[bytes] = ...
    ) -> Optional[Union[_UrlopenRet, addinfourl]]: ...  # undocumented
    def http_error_303(
        self, url: str, fp: IO[str], errcode: int, errmsg: str, headers: Mapping[str, str], data: Optional[bytes] = ...
    ) -> Optional[Union[_UrlopenRet, addinfourl]]: ...  # undocumented
    def http_error_307(
        self, url: str, fp: IO[str], errcode: int, errmsg: str, headers: Mapping[str, str], data: Optional[bytes] = ...
    ) -> Optional[Union[_UrlopenRet, addinfourl]]: ...  # undocumented
    def http_error_401(
        self,
        url: str,
        fp: IO[str],
        errcode: int,
        errmsg: str,
        headers: Mapping[str, str],
        data: Optional[bytes] = ...,
        retry: bool = ...,
    ) -> Optional[_UrlopenRet]: ...  # undocumented
    def http_error_407(
        self,
        url: str,
        fp: IO[str],
        errcode: int,
        errmsg: str,
        headers: Mapping[str, str],
        data: Optional[bytes] = ...,
        retry: bool = ...,
    ) -> Optional[_UrlopenRet]: ...  # undocumented
    def http_error_default(
        self, url: str, fp: IO[bytes], errcode: int, errmsg: str, headers: Mapping[str, str]
    ) -> addinfourl: ...  # undocumented
    def redirect_internal(
        self, url: str, fp: IO[str], errcode: int, errmsg: str, headers: Mapping[str, str], data: Optional[bytes]
    ) -> Optional[_UrlopenRet]: ...  # undocumented
    def retry_http_basic_auth(
        self, url: str, realm: str, data: Optional[bytes] = ...
    ) -> Optional[_UrlopenRet]: ...  # undocumented
    def retry_https_basic_auth(
        self, url: str, realm: str, data: Optional[bytes] = ...
    ) -> Optional[_UrlopenRet]: ...  # undocumented
    def retry_proxy_http_basic_auth(
        self, url: str, realm: str, data: Optional[bytes] = ...
    ) -> Optional[_UrlopenRet]: ...  # undocumented
    def retry_proxy_https_basic_auth(
        self, url: str, realm: str, data: Optional[bytes] = ...
    ) -> Optional[_UrlopenRet]: ...  # undocumented
```
