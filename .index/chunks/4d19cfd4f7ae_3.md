# Chunk: 4d19cfd4f7ae_3

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/styles/defaults.py`
- lines: 209-237
- chunk: 4/4

```
.generic.strong": "bold",
    "pygments.generic.prompt": "bold #000080",
    "pygments.generic.output": "#888",
    "pygments.generic.traceback": "#04d",
    "pygments.error": "border:#ff0000",
}


@memoized()
def default_ui_style() -> BaseStyle:
    """
    Create a default `Style` object.
    """
    return merge_styles(
        [
            Style(PROMPT_TOOLKIT_STYLE),
            Style(COLORS_STYLE),
            Style(WIDGETS_STYLE),
        ]
    )


@memoized()
def default_pygments_style() -> Style:
    """
    Create a `Style` object that contains the default Pygments style.
    """
    return Style.from_dict(PYGMENTS_DEFAULT_STYLE)
```
