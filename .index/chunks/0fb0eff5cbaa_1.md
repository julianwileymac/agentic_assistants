# Chunk: 0fb0eff5cbaa_1

- source: `.venv-lab/Lib/site-packages/send2trash-2.0.0.dist-info/METADATA`
- lines: 55-107
- chunk: 2/2

```
OSX and Linux 
issues and fixes would be most appreciated.

Installation
------------

You can download it with pip:

    python -m pip install -U send2trash

To install with pywin32 or pyobjc required specify the extra `nativeLib`:

    python -m pip install -U send2trash[nativeLib]

or download the source from https://github.com/arsenetar/send2trash and install it with:

    python -m pip install -e .

On systems where Python enforces PEP 668 (e.g., recent Linux distributions),
installing packages into the system Python may be restricted.
Use a virtual environment:

    python -m venv .venv

    GNU/Linux / macOS:

        source .venv/bin/activate

    Windows:

        .venv\Scripts\activate

Usage
-----

>>> from send2trash import send2trash
>>> send2trash('some_file')
>>> send2trash(['some_file1', 'some_file2'])

On Freedesktop platforms (Linux, BSD, etc.), you may not be able to efficiently
trash some files. In these cases, an exception ``send2trash.TrashPermissionError``
is raised, so that the application can handle this case. This inherits from
``PermissionError``. Specifically, this affects
files on a different device to the user's home directory, where the root of the
device does not have a ``.Trash`` directory, and we don't have permission to
create a ``.Trash-$UID`` directory.

For any other problem, ``OSError`` is raised.

.. _PyGObject: https://wiki.gnome.org/PyGObject
.. _GIO: https://developer.gnome.org/gio/
.. _trash specifications from freedesktop.org: http://freedesktop.org/wiki/Specifications/trash-spec/
```
