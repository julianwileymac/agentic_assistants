# Chunk: a64afdbfb071_1

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/2and3/boto/s3/connection.pyi`
- lines: 84-129
- chunk: 2/2

```
res_in: int = ...,
        acl: Optional[Any] = ...,
        success_action_redirect: Optional[Any] = ...,
        max_content_length: Optional[Any] = ...,
        http_method: str = ...,
        fields: Optional[Any] = ...,
        conditions: Optional[Any] = ...,
        storage_class: str = ...,
        server_side_encryption: Optional[Any] = ...,
    ): ...
    def generate_url_sigv4(
        self,
        expires_in,
        method,
        bucket: str = ...,
        key: str = ...,
        headers: Optional[Dict[Text, Text]] = ...,
        force_http: bool = ...,
        response_headers: Optional[Dict[Text, Text]] = ...,
        version_id: Optional[Any] = ...,
        iso_date: Optional[Any] = ...,
    ): ...
    def generate_url(
        self,
        expires_in,
        method,
        bucket: str = ...,
        key: str = ...,
        headers: Optional[Dict[Text, Text]] = ...,
        query_auth: bool = ...,
        force_http: bool = ...,
        response_headers: Optional[Dict[Text, Text]] = ...,
        expires_in_absolute: bool = ...,
        version_id: Optional[Any] = ...,
    ): ...
    def get_all_buckets(self, headers: Optional[Dict[Text, Text]] = ...): ...
    def get_canonical_user_id(self, headers: Optional[Dict[Text, Text]] = ...): ...
    def get_bucket(self, bucket_name: Text, validate: bool = ..., headers: Optional[Dict[Text, Text]] = ...) -> Bucket: ...
    def head_bucket(self, bucket_name, headers: Optional[Dict[Text, Text]] = ...): ...
    def lookup(self, bucket_name, validate: bool = ..., headers: Optional[Dict[Text, Text]] = ...): ...
    def create_bucket(
        self, bucket_name, headers: Optional[Dict[Text, Text]] = ..., location: Any = ..., policy: Optional[Any] = ...
    ): ...
    def delete_bucket(self, bucket, headers: Optional[Dict[Text, Text]] = ...): ...
    def make_request(self, method, bucket: str = ..., key: str = ..., headers: Optional[Any] = ..., data: str = ..., query_args: Optional[Any] = ..., sender: Optional[Any] = ..., override_num_retries: Optional[Any] = ..., retry_handler: Optional[Any] = ..., *args, **kwargs): ...  # type: ignore # https://github.com/python/mypy/issues/1237
```
