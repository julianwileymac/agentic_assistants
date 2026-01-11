# Chunk: b7c8cf727aba_1

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/3/lzma.pyi`
- lines: 98-165
- chunk: 2/2

```
ral["r", "rb"] = ...,
    *,
    format: Optional[int] = ...,
    check: Literal[-1] = ...,
    preset: None = ...,
    filters: Optional[_FilterChain] = ...,
    encoding: None = ...,
    errors: None = ...,
    newline: None = ...,
) -> LZMAFile: ...
@overload
def open(
    filename: _PathOrFile,
    mode: _OpenBinaryWritingMode,
    *,
    format: Optional[int] = ...,
    check: int = ...,
    preset: Optional[int] = ...,
    filters: Optional[_FilterChain] = ...,
    encoding: None = ...,
    errors: None = ...,
    newline: None = ...,
) -> LZMAFile: ...
@overload
def open(
    filename: AnyPath,
    mode: Literal["rt"],
    *,
    format: Optional[int] = ...,
    check: Literal[-1] = ...,
    preset: None = ...,
    filters: Optional[_FilterChain] = ...,
    encoding: Optional[str] = ...,
    errors: Optional[str] = ...,
    newline: Optional[str] = ...,
) -> TextIO: ...
@overload
def open(
    filename: AnyPath,
    mode: _OpenTextWritingMode,
    *,
    format: Optional[int] = ...,
    check: int = ...,
    preset: Optional[int] = ...,
    filters: Optional[_FilterChain] = ...,
    encoding: Optional[str] = ...,
    errors: Optional[str] = ...,
    newline: Optional[str] = ...,
) -> TextIO: ...
@overload
def open(
    filename: _PathOrFile,
    mode: str,
    *,
    format: Optional[int] = ...,
    check: int = ...,
    preset: Optional[int] = ...,
    filters: Optional[_FilterChain] = ...,
    encoding: Optional[str] = ...,
    errors: Optional[str] = ...,
    newline: Optional[str] = ...,
) -> Union[LZMAFile, TextIO]: ...
def compress(
    data: bytes, format: int = ..., check: int = ..., preset: Optional[int] = ..., filters: Optional[_FilterChain] = ...
) -> bytes: ...
def decompress(data: bytes, format: int = ..., memlimit: Optional[int] = ..., filters: Optional[_FilterChain] = ...) -> bytes: ...
def is_check_supported(check: int) -> bool: ...
```
