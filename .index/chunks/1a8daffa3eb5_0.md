# Chunk: 1a8daffa3eb5_0

- source: `.venv-lab/Lib/site-packages/nbformat/v2/nbbase.py`
- lines: 1-101
- chunk: 1/2

```
"""The basic dict based notebook format.

The Python representation of a notebook is a nested structure of
dictionary subclasses that support attribute access.
The functions in this module are merely
helpers to build the structs in the right form.

Authors:

* Brian Granger
"""

# -----------------------------------------------------------------------------
#  Copyright (C) 2008-2011  The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file LICENSE, distributed as part of this software.
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
from __future__ import annotations

from nbformat._struct import Struct

# -----------------------------------------------------------------------------
# Code
# -----------------------------------------------------------------------------


class NotebookNode(Struct):
    """A notebook node object."""


def from_dict(d):
    """Create notebook node(s) from a value."""
    if isinstance(d, dict):
        newd = NotebookNode()
        for k, v in d.items():
            newd[k] = from_dict(v)
        return newd
    if isinstance(d, (tuple, list)):
        return [from_dict(i) for i in d]
    return d


def new_output(
    output_type=None,
    output_text=None,
    output_png=None,
    output_html=None,
    output_svg=None,
    output_latex=None,
    output_json=None,
    output_javascript=None,
    output_jpeg=None,
    prompt_number=None,
    etype=None,
    evalue=None,
    traceback=None,
):
    """Create a new code cell with input and output"""
    output = NotebookNode()
    if output_type is not None:
        output.output_type = str(output_type)

    if output_type != "pyerr":
        if output_text is not None:
            output.text = str(output_text)
        if output_png is not None:
            output.png = bytes(output_png)
        if output_jpeg is not None:
            output.jpeg = bytes(output_jpeg)
        if output_html is not None:
            output.html = str(output_html)
        if output_svg is not None:
            output.svg = str(output_svg)
        if output_latex is not None:
            output.latex = str(output_latex)
        if output_json is not None:
            output.json = str(output_json)
        if output_javascript is not None:
            output.javascript = str(output_javascript)

    if output_type == "pyout" and prompt_number is not None:
        output.prompt_number = int(prompt_number)

    if output_type == "pyerr":
        if etype is not None:
            output.etype = str(etype)
        if evalue is not None:
            output.evalue = str(evalue)
        if traceback is not None:
            output.traceback = [str(frame) for frame in list(traceback)]

    return output


def new_code_cell(
```
