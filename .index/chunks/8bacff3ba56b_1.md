# Chunk: 8bacff3ba56b_1

- source: `.venv-lab/Lib/site-packages/nbformat/v4/nbbase.py`
- lines: 93-172
- chunk: 2/2

```
ntent["execution_count"],
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
            metadata=content["metadata"],
            data=content["data"],
        )
    if msg_type == "error":
        return new_output(
            output_type=msg_type,
            ename=content["ename"],
            evalue=content["evalue"],
            traceback=content["traceback"],
        )
    raise ValueError("Unrecognized output msg type: %r" % msg_type)


def new_code_cell(source="", **kwargs):
    """Create a new code cell"""
    cell = NotebookNode(
        id=random_cell_id(),
        cell_type="code",
        metadata=NotebookNode(),
        execution_count=None,
        source=source,
        outputs=[],
    )
    cell.update(kwargs)

    validate(cell, "code_cell")
    return cell


def new_markdown_cell(source="", **kwargs):
    """Create a new markdown cell"""
    cell = NotebookNode(
        id=random_cell_id(),
        cell_type="markdown",
        source=source,
        metadata=NotebookNode(),
    )
    cell.update(kwargs)

    validate(cell, "markdown_cell")
    return cell


def new_raw_cell(source="", **kwargs):
    """Create a new raw cell"""
    cell = NotebookNode(
        id=random_cell_id(),
        cell_type="raw",
        source=source,
        metadata=NotebookNode(),
    )
    cell.update(kwargs)

    validate(cell, "raw_cell")
    return cell


def new_notebook(**kwargs):
    """Create a new notebook"""
    nb = NotebookNode(
        nbformat=nbformat,
        nbformat_minor=nbformat_minor,
        metadata=NotebookNode(),
        cells=[],
    )
    nb.update(kwargs)
    validate(nb)
    return nb
```
