# Chunk: 8bacff3ba56b_0

- source: `.venv-lab/Lib/site-packages/nbformat/v4/nbbase.py`
- lines: 1-104
- chunk: 1/2

```
"""Python API for composing notebook elements

The Python representation of a notebook is a nested structure of
dictionary subclasses that support attribute access.
The functions in this module are merely helpers to build the structs
in the right form.
"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.
from __future__ import annotations

from nbformat.corpus.words import generate_corpus_id as random_cell_id
from nbformat.notebooknode import NotebookNode

# Change the nbformat_minor and nbformat_schema variables when incrementing the
# nbformat version

# current major version
nbformat = 4

# current minor version
nbformat_minor = 5

# schema files for (major, minor) version tuples. (None, None) means the current version
nbformat_schema = {
    (None, None): "nbformat.v4.schema.json",
    (4, 0): "nbformat.v4.0.schema.json",
    (4, 1): "nbformat.v4.1.schema.json",
    (4, 2): "nbformat.v4.2.schema.json",
    (4, 3): "nbformat.v4.3.schema.json",
    (4, 4): "nbformat.v4.4.schema.json",
    (4, 5): "nbformat.v4.5.schema.json",
}


def validate(node, ref=None):
    """validate a v4 node"""
    from nbformat import validate as validate_orig

    return validate_orig(node, ref=ref, version=nbformat)


def new_output(output_type, data=None, **kwargs):
    """Create a new output, to go in the ``cell.outputs`` list of a code cell."""
    output = NotebookNode(output_type=output_type)

    # populate defaults:
    if output_type == "stream":
        output.name = "stdout"
        output.text = ""
    elif output_type == "display_data":
        output.metadata = NotebookNode()
        output.data = NotebookNode()
    elif output_type == "execute_result":
        output.metadata = NotebookNode()
        output.data = NotebookNode()
        output.execution_count = None
    elif output_type == "error":
        output.ename = "NotImplementedError"
        output.evalue = ""
        output.traceback = []

    # load from args:
    output.update(kwargs)
    if data is not None:
        output.data = data
    # validate
    validate(output, output_type)
    return output


def output_from_msg(msg):
    """Create a NotebookNode for an output from a kernel's IOPub message.

    Returns
    -------
    NotebookNode: the output as a notebook node.

    Raises
    ------
    ValueError: if the message is not an output message.

    """
    msg_type = msg["header"]["msg_type"]
    content = msg["content"]

    if msg_type == "execute_result":
        return new_output(
            output_type=msg_type,
            metadata=content["metadata"],
            data=content["data"],
            execution_count=content["execution_count"],
        )
    if msg_type == "stream":
        return new_output(
            output_type=msg_type,
            name=content["name"],
            text=content["text"],
        )
    if msg_type == "display_data":
        return new_output(
            output_type=msg_type,
```
