# Chunk: 7baed29eb50c_0

- source: `.venv-lab/Lib/site-packages/colorama-0.4.6.dist-info/METADATA`
- lines: 1-76
- chunk: 1/7

```
Metadata-Version: 2.1
Name: colorama
Version: 0.4.6
Summary: Cross-platform colored terminal text.
Project-URL: Homepage, https://github.com/tartley/colorama
Author-email: Jonathan Hartley <tartley@tartley.com>
License-File: LICENSE.txt
Keywords: ansi,color,colour,crossplatform,terminal,text,windows,xplatform
Classifier: Development Status :: 5 - Production/Stable
Classifier: Environment :: Console
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: BSD License
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.7
Classifier: Programming Language :: Python :: 3.8
Classifier: Programming Language :: Python :: 3.9
Classifier: Programming Language :: Python :: 3.10
Classifier: Programming Language :: Python :: Implementation :: CPython
Classifier: Programming Language :: Python :: Implementation :: PyPy
Classifier: Topic :: Terminals
Requires-Python: !=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*,!=3.6.*,>=2.7
Description-Content-Type: text/x-rst

.. image:: https://img.shields.io/pypi/v/colorama.svg
    :target: https://pypi.org/project/colorama/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/colorama.svg
    :target: https://pypi.org/project/colorama/
    :alt: Supported Python versions

.. image:: https://github.com/tartley/colorama/actions/workflows/test.yml/badge.svg
    :target: https://github.com/tartley/colorama/actions/workflows/test.yml
    :alt: Build Status

Colorama
========

Makes ANSI escape character sequences (for producing colored terminal text and
cursor positioning) work under MS Windows.

.. |donate| image:: https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif
  :target: https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=2MZ9D2GMLYCUJ&item_name=Colorama&currency_code=USD
  :alt: Donate with Paypal

`PyPI for releases <https://pypi.org/project/colorama/>`_ |
`Github for source <https://github.com/tartley/colorama>`_ |
`Colorama for enterprise on Tidelift <https://github.com/tartley/colorama/blob/master/ENTERPRISE.md>`_

If you find Colorama useful, please |donate| to the authors. Thank you!

Installation
------------

Tested on CPython 2.7, 3.7, 3.8, 3.9 and 3.10 and Pypy 2.7 and 3.8.

No requirements other than the standard library.

.. code-block:: bash

    pip install colorama
    # or
    conda install -c anaconda colorama

Description
-----------

ANSI escape character sequences have long been used to produce colored terminal
text and cursor positioning on Unix and Macs. Colorama makes this work on
Windows, too, by wrapping ``stdout``, stripping ANSI sequences it finds (which
would appear as gobbledygook in the output), and converting them into the
```
