# Chunk: df81e6bcba34_2

- source: `.venv-lab/Lib/site-packages/_distutils_hack/__init__.py`
- lines: 178-240
- chunk: 3/3

```
mes may not have __file__ (#2940)
        return frame.f_globals.get('__file__', '').endswith('setup.py')

    def spec_for_sensitive_tests(self):
        """
        Ensure stdlib distutils when running select tests under CPython.

        python/cpython#91169
        """
        clear_distutils()
        self.spec_for_distutils = lambda: None

    sensitive_tests = (
        [
            'test.test_distutils',
            'test.test_peg_generator',
            'test.test_importlib',
        ]
        if sys.version_info < (3, 10)
        else [
            'test.test_distutils',
        ]
    )


for name in DistutilsMetaFinder.sensitive_tests:
    setattr(
        DistutilsMetaFinder,
        f'spec_for_{name}',
        DistutilsMetaFinder.spec_for_sensitive_tests,
    )


DISTUTILS_FINDER = DistutilsMetaFinder()


def add_shim():
    DISTUTILS_FINDER in sys.meta_path or insert_shim()


class shim:
    def __enter__(self) -> None:
        insert_shim()

    def __exit__(self, exc: object, value: object, tb: object) -> None:
        _remove_shim()


def insert_shim():
    sys.meta_path.insert(0, DISTUTILS_FINDER)


def _remove_shim():
    try:
        sys.meta_path.remove(DISTUTILS_FINDER)
    except ValueError:
        pass


if sys.version_info < (3, 12):
    # DistutilsMetaFinder can only be disabled in Python < 3.12 (PEP 632)
    remove_shim = _remove_shim
```
