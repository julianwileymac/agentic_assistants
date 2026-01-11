# Chunk: 8bbe9fa7b94d_0

- source: `.venv-lab/Lib/site-packages/decorator-5.2.1.dist-info/METADATA`
- lines: 1-91
- chunk: 1/2

```
Metadata-Version: 2.2
Name: decorator
Version: 5.2.1
Summary: Decorators for Humans
Author-email: Michele Simionato <michele.simionato@gmail.com>
License: BSD-2-Clause
Keywords: decorators
Classifier: Development Status :: 5 - Production/Stable
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: BSD License
Classifier: Natural Language :: English
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 3.8
Classifier: Programming Language :: Python :: 3.9
Classifier: Programming Language :: Python :: 3.10
Classifier: Programming Language :: Python :: 3.11
Classifier: Programming Language :: Python :: 3.12
Classifier: Programming Language :: Python :: 3.13
Classifier: Programming Language :: Python :: Implementation :: CPython
Classifier: Topic :: Software Development :: Libraries
Classifier: Topic :: Utilities
Requires-Python: >=3.8
Description-Content-Type: text/x-rst
License-File: LICENSE.txt

Decorators for Humans
=====================

The goal of the decorator module is to make it easy to define
signature-preserving function decorators and decorator factories.
It also includes an implementation of multiple dispatch and other niceties
(please check the docs). It is released under a two-clauses
BSD license, i.e. basically you can do whatever you want with it but I am not
responsible.

Installation
-------------

If you are lazy, just perform

 ``$ pip install decorator``

which will install just the module on your system.

If you prefer to install the full distribution from source, including
the documentation, clone the `GitHub repo`_ or download the tarball_, unpack it and run

 ``$ pip install .``

in the main directory, possibly as superuser.

.. _tarball: https://pypi.org/project/decorator/#files
.. _GitHub repo: https://github.com/micheles/decorator

Testing
--------

If you have the source code installation you can run the tests with

 `$ python src/tests/test.py -v`

or (if you have setuptools installed)

 `$ python setup.py test`

Notice that you may run into trouble if in your system there
is an older version of the decorator module; in such a case remove the
old version. It is safe even to copy the module `decorator.py` over
an existing one, since we kept backward-compatibility for a long time.

Repository
---------------

The project is hosted on GitHub. You can look at the source here:

 https://github.com/micheles/decorator

Documentation
---------------

The documentation has been moved to https://github.com/micheles/decorator/blob/master/docs/documentation.md

From there you can get a PDF version by simply using the print
functionality of your browser.

Here is the documentation for previous versions of the module:

https://github.com/micheles/decorator/blob/4.3.2/docs/tests.documentation.rst
https://github.com/micheles/decorator/blob/4.2.1/docs/tests.documentation.rst
```
