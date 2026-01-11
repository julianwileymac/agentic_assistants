# Chunk: ccc6b5bec4ab_1

- source: `.venv-lab/Lib/site-packages/mistune/plugins/formatting.py`
- lines: 83-184
- chunk: 2/2

```
 state.copy()
    new_state.src = text[1:-1].replace("\\ ", " ")
    children = inline.render(new_state)
    state.append_token({"type": tok_type, "children": children})
    return m.end()


def strikethrough(md: "Markdown") -> None:
    """A mistune plugin to support strikethrough. Spec defined by
    GitHub flavored Markdown and commonly used by many parsers:

    .. code-block:: text

        ~~This was mistaken text~~

    It will be converted into HTML:

    .. code-block:: html

        <del>This was mistaken text</del>

    :param md: Markdown instance
    """
    md.inline.register(
        "strikethrough",
        r"~~(?=[^\s~])",
        parse_strikethrough,
        before="link",
    )
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("strikethrough", render_strikethrough)


def mark(md: "Markdown") -> None:
    """A mistune plugin to add ``<mark>`` tag. Spec defined at
    https://facelessuser.github.io/pymdown-extensions/extensions/mark/:

    .. code-block:: text

        ==mark me== ==mark \\=\\= equal==

    :param md: Markdown instance
    """
    md.inline.register(
        "mark",
        r"==(?=[^\s=])",
        parse_mark,
        before="link",
    )
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("mark", render_mark)


def insert(md: "Markdown") -> None:
    """A mistune plugin to add ``<ins>`` tag. Spec defined at
    https://facelessuser.github.io/pymdown-extensions/extensions/caret/#insert:

    .. code-block:: text

        ^^insert me^^

    :param md: Markdown instance
    """
    md.inline.register(
        "insert",
        r"\^\^(?=[^\s\^])",
        parse_insert,
        before="link",
    )
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("insert", render_insert)


def superscript(md: "Markdown") -> None:
    """A mistune plugin to add ``<sup>`` tag. Spec defined at
    https://pandoc.org/MANUAL.html#superscripts-and-subscripts:

    .. code-block:: text

        2^10^ is 1024.

    :param md: Markdown instance
    """
    md.inline.register("superscript", SUPERSCRIPT_PATTERN, parse_superscript, before="linebreak")
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("superscript", render_superscript)


def subscript(md: "Markdown") -> None:
    """A mistune plugin to add ``<sub>`` tag. Spec defined at
    https://pandoc.org/MANUAL.html#superscripts-and-subscripts:

    .. code-block:: text

        H~2~O is a liquid.

    :param md: Markdown instance
    """
    md.inline.register("subscript", SUBSCRIPT_PATTERN, parse_subscript, before="linebreak")
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("subscript", render_subscript)
```
