# Chunk: d64dc2afde6f_0

- source: `.venv-lab/Lib/site-packages/pip/_vendor/certifi/__main__.py`
- lines: 1-13
- chunk: 1/1

```
import argparse

from pip._vendor.certifi import contents, where

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--contents", action="store_true")
args = parser.parse_args()

if args.contents:
    print(contents())
else:
    print(where())
```
