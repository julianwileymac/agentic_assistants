# Chunk: bc8b3b512ebb_1

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/http/cookiejar.pyi`
- lines: 61-130
- chunk: 2/2

```

    DomainLiberal: int
    DomainStrict: int
    def __init__(
        self,
        blocked_domains: Optional[Sequence[str]] = ...,
        allowed_domains: Optional[Sequence[str]] = ...,
        netscape: bool = ...,
        rfc2965: bool = ...,
        rfc2109_as_netscape: Optional[bool] = ...,
        hide_cookie2: bool = ...,
        strict_domain: bool = ...,
        strict_rfc2965_unverifiable: bool = ...,
        strict_ns_unverifiable: bool = ...,
        strict_ns_domain: int = ...,
        strict_ns_set_initial_dollar: bool = ...,
        strict_ns_set_path: bool = ...,
    ) -> None: ...
    def blocked_domains(self) -> Tuple[str, ...]: ...
    def set_blocked_domains(self, blocked_domains: Sequence[str]) -> None: ...
    def is_blocked(self, domain: str) -> bool: ...
    def allowed_domains(self) -> Optional[Tuple[str, ...]]: ...
    def set_allowed_domains(self, allowed_domains: Optional[Sequence[str]]) -> None: ...
    def is_not_allowed(self, domain: str) -> bool: ...

class Cookie:
    version: Optional[int]
    name: str
    value: Optional[str]
    port: Optional[str]
    path: str
    path_specified: bool
    secure: bool
    expires: Optional[int]
    discard: bool
    comment: Optional[str]
    comment_url: Optional[str]
    rfc2109: bool
    port_specified: bool
    domain: str  # undocumented
    domain_specified: bool
    domain_initial_dot: bool
    def __init__(
        self,
        version: Optional[int],
        name: str,
        value: Optional[str],  # undocumented
        port: Optional[str],
        port_specified: bool,
        domain: str,
        domain_specified: bool,
        domain_initial_dot: bool,
        path: str,
        path_specified: bool,
        secure: bool,
        expires: Optional[int],
        discard: bool,
        comment: Optional[str],
        comment_url: Optional[str],
        rest: Dict[str, str],
        rfc2109: bool = ...,
    ) -> None: ...
    def has_nonstandard_attr(self, name: str) -> bool: ...
    @overload
    def get_nonstandard_attr(self, name: str) -> Optional[str]: ...
    @overload
    def get_nonstandard_attr(self, name: str, default: _T = ...) -> Union[str, _T]: ...
    def set_nonstandard_attr(self, name: str, value: str) -> None: ...
    def is_expired(self, now: int = ...) -> bool: ...
```
