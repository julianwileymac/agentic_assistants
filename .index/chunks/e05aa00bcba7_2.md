# Chunk: e05aa00bcba7_2

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2and3/ftplib.pyi`
- lines: 140-166
- chunk: 3/3

```
..) -> str: ...
    def auth(self) -> str: ...
    def prot_p(self) -> str: ...
    def prot_c(self) -> str: ...
    if sys.version_info >= (3, 3):
        def ccc(self) -> str: ...

if sys.version_info < (3,):
    class Netrc:
        def __init__(self, filename: Optional[Text] = ...) -> None: ...
        def get_hosts(self) -> List[str]: ...
        def get_account(self, host: Text) -> Tuple[Optional[str], Optional[str], Optional[str]]: ...
        def get_macros(self) -> List[str]: ...
        def get_macro(self, macro: Text) -> Tuple[str, ...]: ...

def parse150(resp: str) -> Optional[int]: ...  # undocumented
def parse227(resp: str) -> Tuple[str, int]: ...  # undocumented
def parse229(resp: str, peer: Any) -> Tuple[str, int]: ...  # undocumented
def parse257(resp: str) -> str: ...  # undocumented
def ftpcp(
    source: FTP,
    sourcename: str,
    target: FTP,
    targetname: str = ...,
    type: Literal["A", "I"] = ...,
) -> None: ...  # undocumented
```
