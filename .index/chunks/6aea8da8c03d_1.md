# Chunk: 6aea8da8c03d_1

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/_typeshed/__init__.pyi`
- lines: 96-184
- chunk: 2/2

```
   "a+t",
    "+at",
    "ta+",
    "t+a",
    "+ta",
    "x",
    "x+",
    "+x",
    "xt",
    "tx",
    "xt+",
    "x+t",
    "+xt",
    "tx+",
    "t+x",
    "+tx",
    "U",
    "rU",
    "Ur",
    "rtU",
    "rUt",
    "Urt",
    "trU",
    "tUr",
    "Utr",
]
OpenBinaryModeUpdating = Literal[
    "rb+",
    "r+b",
    "+rb",
    "br+",
    "b+r",
    "+br",
    "wb+",
    "w+b",
    "+wb",
    "bw+",
    "b+w",
    "+bw",
    "ab+",
    "a+b",
    "+ab",
    "ba+",
    "b+a",
    "+ba",
    "xb+",
    "x+b",
    "+xb",
    "bx+",
    "b+x",
    "+bx",
]
OpenBinaryModeWriting = Literal["wb", "bw", "ab", "ba", "xb", "bx"]
OpenBinaryModeReading = Literal["rb", "br", "rbU", "rUb", "Urb", "brU", "bUr", "Ubr"]
OpenBinaryMode = Union[OpenBinaryModeUpdating, OpenBinaryModeReading, OpenBinaryModeWriting]

class HasFileno(Protocol):
    def fileno(self) -> int: ...

FileDescriptor = int
FileDescriptorLike = Union[int, HasFileno]

class SupportsRead(Protocol[_T_co]):
    def read(self, __length: int = ...) -> _T_co: ...

class SupportsReadline(Protocol[_T_co]):
    def readline(self, __length: int = ...) -> _T_co: ...

class SupportsNoArgReadline(Protocol[_T_co]):
    def readline(self) -> _T_co: ...

class SupportsWrite(Protocol[_T_contra]):
    def write(self, __s: _T_contra) -> int: ...

if sys.version_info >= (3,):
    ReadableBuffer = Union[bytes, bytearray, memoryview, array.array, mmap.mmap]
    WriteableBuffer = Union[bytearray, memoryview, array.array, mmap.mmap]
else:
    ReadableBuffer = Union[bytes, bytearray, memoryview, array.array, mmap.mmap, buffer]
    WriteableBuffer = Union[bytearray, memoryview, array.array, mmap.mmap, buffer]

if sys.version_info >= (3, 10):
    from types import NoneType as NoneType
else:
    # Used by type checkers for checks involving None (does not exist at runtime)
    @final
    class NoneType:
        def __bool__(self) -> Literal[False]: ...
```
