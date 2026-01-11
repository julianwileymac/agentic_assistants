# Chunk: 4d19cfd4f7ae_1

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/styles/defaults.py`
- lines: 74-150
- chunk: 2/4

```
:#444444"),
    ("completion-menu.completion fuzzymatch.inside", "bold"),
    ("completion-menu.completion fuzzymatch.inside.character", "underline"),
    ("completion-menu.completion.current fuzzymatch.outside", "fg:default"),
    ("completion-menu.completion.current fuzzymatch.inside", "nobold"),
    # Styling of readline-like completions.
    ("readline-like-completions", ""),
    ("readline-like-completions.completion", ""),
    ("readline-like-completions.completion fuzzymatch.outside", "#888888"),
    ("readline-like-completions.completion fuzzymatch.inside", ""),
    ("readline-like-completions.completion fuzzymatch.inside.character", "underline"),
    # Scrollbars.
    ("scrollbar.background", "bg:#aaaaaa"),
    ("scrollbar.button", "bg:#444444"),
    ("scrollbar.arrow", "noinherit bold"),
    # Start/end of scrollbars. Adding 'underline' here provides a nice little
    # detail to the progress bar, but it doesn't look good on all terminals.
    # ('scrollbar.start',                          'underline #ffffff'),
    # ('scrollbar.end',                            'underline #000000'),
    # Auto suggestion text.
    ("auto-suggestion", "#666666"),
    # Trailing whitespace and tabs.
    ("trailing-whitespace", "#999999"),
    ("tab", "#999999"),
    # When Control-C/D has been pressed. Grayed.
    ("aborting", "#888888 bg:default noreverse noitalic nounderline noblink"),
    ("exiting", "#888888 bg:default noreverse noitalic nounderline noblink"),
    # Entering a Vi digraph.
    ("digraph", "#4444ff"),
    # Control characters, like ^C, ^X.
    ("control-character", "ansiblue"),
    # Non-breaking space.
    ("nbsp", "underline ansiyellow"),
    # Default styling of HTML elements.
    ("i", "italic"),
    ("u", "underline"),
    ("s", "strike"),
    ("b", "bold"),
    ("em", "italic"),
    ("strong", "bold"),
    ("del", "strike"),
    ("hidden", "hidden"),
    # It should be possible to use the style names in HTML.
    # <reverse>...</reverse>  or <noreverse>...</noreverse>.
    ("italic", "italic"),
    ("underline", "underline"),
    ("strike", "strike"),
    ("bold", "bold"),
    ("reverse", "reverse"),
    ("noitalic", "noitalic"),
    ("nounderline", "nounderline"),
    ("nostrike", "nostrike"),
    ("nobold", "nobold"),
    ("noreverse", "noreverse"),
    # Prompt bottom toolbar
    ("bottom-toolbar", "reverse"),
]


# Style that will turn for instance the class 'red' into 'red'.
COLORS_STYLE = [(name, "fg:" + name) for name in ANSI_COLOR_NAMES] + [
    (name.lower(), "fg:" + name) for name in NAMED_COLORS
]


WIDGETS_STYLE = [
    # Dialog windows.
    ("dialog", "bg:#4444ff"),
    ("dialog.body", "bg:#ffffff #000000"),
    ("dialog.body text-area", "bg:#cccccc"),
    ("dialog.body text-area last-line", "underline"),
    ("dialog frame.label", "#ff0000 bold"),
    # Scrollbars in dialogs.
    ("dialog.body scrollbar.background", ""),
    ("dialog.body scrollbar.button", "bg:#000000"),
    ("dialog.body scrollbar.arrow", ""),
```
