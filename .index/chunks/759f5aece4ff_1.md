# Chunk: 759f5aece4ff_1

- source: `.venv-lab/Lib/site-packages/setuptools/tests/test_bdist_wheel.py`
- lines: 106-216
- chunk: 2/9

```
__init__.py": "def main(): return"},
    },
    "headers-dist": {
        "setup.py": cleandoc(
            """
            from setuptools import setup

            setup(
                name="headers.dist",
                version="0.1",
                description="A distribution with headers",
                headers=["header.h"],
            )
            """
        ),
        "headersdist.py": "",
        "header.h": "",
    },
    "commasinfilenames-dist": {
        "setup.py": cleandoc(
            """
            from setuptools import setup

            setup(
                name="testrepo",
                version="0.1",
                packages=["mypackage"],
                description="A test package with commas in file names",
                include_package_data=True,
                package_data={"mypackage.data": ["*"]},
            )
            """
        ),
        "mypackage": {
            "__init__.py": "",
            "data": {"__init__.py": "", "1,2,3.txt": ""},
        },
        "testrepo-0.1.0": {
            "mypackage": {"__init__.py": ""},
        },
    },
    "unicode-dist": {
        "setup.py": cleandoc(
            """
            from setuptools import setup

            setup(
                name="unicode.dist",
                version="0.1",
                description="A testing distribution \N{SNOWMAN}",
                packages=["unicodedist"],
                zip_safe=True,
            )
            """
        ),
        "unicodedist": {"__init__.py": "", "åäö_日本語.py": ""},
    },
    "utf8-metadata-dist": {
        "setup.cfg": cleandoc(
            """
            [metadata]
            name = utf8-metadata-dist
            version = 42
            author_email = "John X. Ãørçeč" <john@utf8.org>, Γαμα קּ 東 <gama@utf8.org>
            long_description = file: README.rst
            """
        ),
        "README.rst": "UTF-8 描述 説明",
    },
    "licenses-dist": {
        "setup.cfg": cleandoc(
            """
            [metadata]
            name = licenses-dist
            version = 1.0
            license_files = **/LICENSE
            """
        ),
        "LICENSE": "",
        "src": {
            "vendor": {"LICENSE": ""},
        },
    },
}


if sys.platform != "win32":
    # ABI3 extensions don't really work on Windows
    EXAMPLES["abi3extension-dist"] = {
        "setup.py": cleandoc(
            """
            from setuptools import Extension, setup

            setup(
                name="extension.dist",
                version="0.1",
                description="A testing distribution \N{SNOWMAN}",
                ext_modules=[
                    Extension(
                        name="extension", sources=["extension.c"], py_limited_api=True
                    )
                ],
            )
            """
        ),
        "setup.cfg": "[bdist_wheel]\npy_limited_api=cp32",
        "extension.c": "#define Py_LIMITED_API 0x03020000\n#include <Python.h>",
    }
```
