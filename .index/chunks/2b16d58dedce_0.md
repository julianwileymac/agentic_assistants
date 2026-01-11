# Chunk: 2b16d58dedce_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/linux_and_mac/compile_mac.sh`
- lines: 1-15
- chunk: 1/1

```
#!/bin/bash
set -e
SRC="$(dirname "$0")/.."

g++ -fPIC -D_REENTRANT -std=c++11 -D_FORTIFY_SOURCE=2 -arch arm64 -c -o "$SRC/attach_arm64.o" "$SRC/linux_and_mac/attach.cpp"
g++ -dynamiclib -nostartfiles -arch arm64 -o "$SRC/attach_arm64.dylib" "$SRC/attach_arm64.o" -lc
rm "$SRC/attach_arm64.o"

g++ -fPIC -D_REENTRANT -std=c++11 -D_FORTIFY_SOURCE=2 -arch x86_64 -c -o "$SRC/attach_x86_64.o" "$SRC/linux_and_mac/attach.cpp"
g++ -dynamiclib -nostartfiles -arch x86_64 -o "$SRC/attach_x86_64.dylib" "$SRC/attach_x86_64.o" -lc
rm "$SRC/attach_x86_64.o"

lipo -create "$SRC/attach_arm64.dylib" "$SRC/attach_x86_64.dylib" -output "$SRC/attach.dylib"
rm "$SRC/attach_arm64.dylib" "$SRC/attach_x86_64.dylib"
```
