# Chunk: cb9388bdfca9_1

- source: `.venv-lab/Lib/site-packages/nbconvert/utils/io.py`
- lines: 107-121
- chunk: 2/2

```
_dst = dst + f"-temp-{random.randint(1, 16**4):04X}"  # noqa: S311
        try:
            link_or_copy(src, new_dst)
        except BaseException:
            try:
                os.remove(new_dst)
            except OSError:
                pass
            raise
        os.rename(new_dst, dst)
    elif link_errno != 0:
        # Either link isn't supported, or the filesystem doesn't support
        # linking, or 'src' and 'dst' are on different filesystems.
        shutil.copy(src, dst)
```
