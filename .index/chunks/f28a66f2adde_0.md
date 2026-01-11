# Chunk: f28a66f2adde_0

- source: `.venv-lab/Lib/site-packages/stack_data-0.6.3.dist-info/METADATA`
- lines: 1-77
- chunk: 1/7

```
Metadata-Version: 2.1
Name: stack-data
Version: 0.6.3
Summary: Extract data from python stack frames and tracebacks for informative displays
Home-page: http://github.com/alexmojaki/stack_data
Author: Alex Hall
Author-email: alex.mojaki@gmail.com
License: MIT
Classifier: Intended Audience :: Developers
Classifier: Programming Language :: Python :: 3.5
Classifier: Programming Language :: Python :: 3.6
Classifier: Programming Language :: Python :: 3.7
Classifier: Programming Language :: Python :: 3.8
Classifier: Programming Language :: Python :: 3.9
Classifier: Programming Language :: Python :: 3.10
Classifier: Programming Language :: Python :: 3.11
Classifier: Programming Language :: Python :: 3.12
Classifier: License :: OSI Approved :: MIT License
Classifier: Operating System :: OS Independent
Classifier: Topic :: Software Development :: Debuggers
Description-Content-Type: text/markdown
License-File: LICENSE.txt
Requires-Dist: executing >=1.2.0
Requires-Dist: asttokens >=2.1.0
Requires-Dist: pure-eval
Provides-Extra: tests
Requires-Dist: pytest ; extra == 'tests'
Requires-Dist: typeguard ; extra == 'tests'
Requires-Dist: pygments ; extra == 'tests'
Requires-Dist: littleutils ; extra == 'tests'
Requires-Dist: cython ; extra == 'tests'

# stack_data

[![Tests](https://github.com/alexmojaki/stack_data/actions/workflows/pytest.yml/badge.svg)](https://github.com/alexmojaki/stack_data/actions/workflows/pytest.yml) [![Coverage Status](https://coveralls.io/repos/github/alexmojaki/stack_data/badge.svg?branch=master)](https://coveralls.io/github/alexmojaki/stack_data?branch=master) [![Supports Python versions 3.5+](https://img.shields.io/pypi/pyversions/stack_data.svg)](https://pypi.python.org/pypi/stack_data)

This is a library that extracts data from stack frames and tracebacks, particularly to display more useful tracebacks than the default. It powers the tracebacks in IPython and [futurecoder](https://futurecoder.io/):

![futurecoder example](https://futurecoder.io/static/img/features/traceback.png)

You can install it from PyPI:

    pip install stack_data
    
## Basic usage

Here's some code we'd like to inspect:

```python
def foo():
    result = []
    for i in range(5):
        row = []
        result.append(row)
        print_stack()
        for j in range(5):
            row.append(i * j)
    return result
```

Note that `foo` calls a function `print_stack()`. In reality we can imagine that an exception was raised at this line, or a debugger stopped there, but this is easy to play with directly. Here's a basic implementation:

```python
import inspect
import stack_data


def print_stack():
    frame = inspect.currentframe().f_back
    frame_info = stack_data.FrameInfo(frame)
    print(f"{frame_info.code.co_name} at line {frame_info.lineno}")
    print("-----------")
    for line in frame_info.lines:
        print(f"{'-->' if line.is_current else '   '} {line.lineno:4} | {line.render()}")
```
```
