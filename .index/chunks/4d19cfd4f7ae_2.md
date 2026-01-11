# Chunk: 4d19cfd4f7ae_2

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/styles/defaults.py`
- lines: 143-222
- chunk: 3/4

```
g.body text-area", "bg:#cccccc"),
    ("dialog.body text-area last-line", "underline"),
    ("dialog frame.label", "#ff0000 bold"),
    # Scrollbars in dialogs.
    ("dialog.body scrollbar.background", ""),
    ("dialog.body scrollbar.button", "bg:#000000"),
    ("dialog.body scrollbar.arrow", ""),
    ("dialog.body scrollbar.start", "nounderline"),
    ("dialog.body scrollbar.end", "nounderline"),
    # Buttons.
    ("button", ""),
    ("button.arrow", "bold"),
    ("button.focused", "bg:#aa0000 #ffffff"),
    # Menu bars.
    ("menu-bar", "bg:#aaaaaa #000000"),
    ("menu-bar.selected-item", "bg:#ffffff #000000"),
    ("menu", "bg:#888888 #ffffff"),
    ("menu.border", "#aaaaaa"),
    ("menu.border shadow", "#444444"),
    # Shadows.
    ("dialog shadow", "bg:#000088"),
    ("dialog.body shadow", "bg:#aaaaaa"),
    ("progress-bar", "bg:#000088"),
    ("progress-bar.used", "bg:#ff0000"),
]


# The default Pygments style, include this by default in case a Pygments lexer
# is used.
PYGMENTS_DEFAULT_STYLE = {
    "pygments.whitespace": "#bbbbbb",
    "pygments.comment": "italic #408080",
    "pygments.comment.preproc": "noitalic #bc7a00",
    "pygments.keyword": "bold #008000",
    "pygments.keyword.pseudo": "nobold",
    "pygments.keyword.type": "nobold #b00040",
    "pygments.operator": "#666666",
    "pygments.operator.word": "bold #aa22ff",
    "pygments.name.builtin": "#008000",
    "pygments.name.function": "#0000ff",
    "pygments.name.class": "bold #0000ff",
    "pygments.name.namespace": "bold #0000ff",
    "pygments.name.exception": "bold #d2413a",
    "pygments.name.variable": "#19177c",
    "pygments.name.constant": "#880000",
    "pygments.name.label": "#a0a000",
    "pygments.name.entity": "bold #999999",
    "pygments.name.attribute": "#7d9029",
    "pygments.name.tag": "bold #008000",
    "pygments.name.decorator": "#aa22ff",
    # Note: In Pygments, Token.String is an alias for Token.Literal.String,
    #       and Token.Number as an alias for Token.Literal.Number.
    "pygments.literal.string": "#ba2121",
    "pygments.literal.string.doc": "italic",
    "pygments.literal.string.interpol": "bold #bb6688",
    "pygments.literal.string.escape": "bold #bb6622",
    "pygments.literal.string.regex": "#bb6688",
    "pygments.literal.string.symbol": "#19177c",
    "pygments.literal.string.other": "#008000",
    "pygments.literal.number": "#666666",
    "pygments.generic.heading": "bold #000080",
    "pygments.generic.subheading": "bold #800080",
    "pygments.generic.deleted": "#a00000",
    "pygments.generic.inserted": "#00a000",
    "pygments.generic.error": "#ff0000",
    "pygments.generic.emph": "italic",
    "pygments.generic.strong": "bold",
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
```
