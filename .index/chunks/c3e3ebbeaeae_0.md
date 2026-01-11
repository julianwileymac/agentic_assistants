# Chunk: c3e3ebbeaeae_0

- source: `.venv-lab/Lib/site-packages/jedi/third_party/typeshed/third_party/3/jwt/contrib/algorithms/pycrypto.pyi`
- lines: 1-11
- chunk: 1/1

```
import hashlib
from typing import Any

from jwt.algorithms import Algorithm

class RSAAlgorithm(Algorithm[Any]):
    SHA256: hashlib._Hash
    SHA384: hashlib._Hash
    SHA512: hashlib._Hash
    def __init__(self, hash_alg: hashlib._Hash) -> None: ...
```
