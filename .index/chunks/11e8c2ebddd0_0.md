# Chunk: 11e8c2ebddd0_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/linux_and_mac/compile_linux.sh`
- lines: 1-12
- chunk: 1/1

```
set -e

ARCH="$(uname -m)"
case $ARCH in
    i*86) SUFFIX=x86;;
    x86_64*) SUFFIX=amd64;;
    *) echo >&2 "unsupported: $ARCH"; exit 1;;
esac

SRC="$(dirname "$0")/.."
g++ -std=c++11 -shared -fPIC -O2 -D_FORTIFY_SOURCE=2 -nostartfiles -fstack-protector-strong $SRC/linux_and_mac/attach.cpp -o $SRC/attach_linux_$SUFFIX.so
```
