# Chunk: df9a64bd0ca0_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/stdlib/2/sha.pyi`
- lines: 1-11
- chunk: 1/1

```
class sha(object):
    def update(self, arg: str) -> None: ...
    def digest(self) -> str: ...
    def hexdigest(self) -> str: ...
    def copy(self) -> sha: ...

def new(string: str = ...) -> sha: ...

blocksize: int
digest_size: int
```
