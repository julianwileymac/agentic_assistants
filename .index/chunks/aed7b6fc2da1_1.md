# Chunk: aed7b6fc2da1_1

- source: `.venv-lab/Lib/site-packages/anyio-4.12.0.dist-info/METADATA`
- lines: 55-97
- chunk: 2/2

```
nstead of asyncio's, you can read about it
`here <https://anyio.readthedocs.io/en/stable/why.html>`_.

Documentation
-------------

View full documentation at: https://anyio.readthedocs.io/

Features
--------

AnyIO offers the following functionality:

* Task groups (nurseries_ in trio terminology)
* High-level networking (TCP, UDP and UNIX sockets)

  * `Happy eyeballs`_ algorithm for TCP connections (more robust than that of asyncio on Python
    3.8)
  * async/await style UDP sockets (unlike asyncio where you still have to use Transports and
    Protocols)

* A versatile API for byte streams and object streams
* Inter-task synchronization and communication (locks, conditions, events, semaphores, object
  streams)
* Worker threads
* Subprocesses
* Subinterpreter support for code parallelization (on Python 3.13 and later)
* Asynchronous file I/O (using worker threads)
* Signal handling
* Asynchronous version of the functools_ module

AnyIO also comes with its own pytest_ plugin which also supports asynchronous fixtures.
It even works with the popular Hypothesis_ library.

.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _Trio: https://github.com/python-trio/trio
.. _structured concurrency: https://en.wikipedia.org/wiki/Structured_concurrency
.. _nurseries: https://trio.readthedocs.io/en/stable/reference-core.html#nurseries-and-spawning
.. _Happy eyeballs: https://en.wikipedia.org/wiki/Happy_Eyeballs
.. _pytest: https://docs.pytest.org/en/latest/
.. _functools: https://docs.python.org/3/library/functools.html
.. _Hypothesis: https://hypothesis.works/
```
