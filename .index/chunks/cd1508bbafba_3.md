# Chunk: cd1508bbafba_3

- source: `.venv-lab/Lib/site-packages/IPython/terminal/shortcuts/__init__.py`
- lines: 275-383
- chunk: 4/7

```
s_suggestion` here to allow resuming if no suggestion
        "default_buffer_focused & emacs_like_insert_mode",
    ),
    Binding(
        auto_suggest.resume_hinting,
        ["right"],
        "is_cursor_at_the_end_of_line"
        " & default_buffer_focused"
        " & emacs_like_insert_mode"
        " & pass_through",
    ),
]


SIMPLE_CONTROL_BINDINGS = [
    Binding(cmd, [key], "vi_insert_mode & default_buffer_focused & ebivim")
    for key, cmd in {
        "c-a": nc.beginning_of_line,
        "c-b": nc.backward_char,
        "c-k": nc.kill_line,
        "c-w": nc.backward_kill_word,
        "c-y": nc.yank,
        "c-_": nc.undo,
    }.items()
]


ALT_AND_COMOBO_CONTROL_BINDINGS = [
    Binding(cmd, list(keys), "vi_insert_mode & default_buffer_focused & ebivim")
    for keys, cmd in {
        # Control Combos
        ("c-x", "c-e"): nc.edit_and_execute,
        ("c-x", "e"): nc.edit_and_execute,
        # Alt
        ("escape", "b"): nc.backward_word,
        ("escape", "c"): nc.capitalize_word,
        ("escape", "d"): nc.kill_word,
        ("escape", "h"): nc.backward_kill_word,
        ("escape", "l"): nc.downcase_word,
        ("escape", "u"): nc.uppercase_word,
        ("escape", "y"): nc.yank_pop,
        ("escape", "."): nc.yank_last_arg,
    }.items()
]


def add_binding(bindings: KeyBindings, binding: Binding):
    bindings.add(
        *binding.keys,
        **({"filter": binding.filter} if binding.filter is not None else {}),
    )(binding.command)


def create_ipython_shortcuts(shell, skip=None) -> KeyBindings:
    """Set up the prompt_toolkit keyboard shortcuts for IPython.

    Parameters
    ----------
    shell: InteractiveShell
        The current IPython shell Instance
    skip: List[Binding]
        Bindings to skip.

    Returns
    -------
    KeyBindings
        the keybinding instance for prompt toolkit.

    """
    kb = KeyBindings()
    skip = skip or []
    for binding in KEY_BINDINGS:
        skip_this_one = False
        for to_skip in skip:
            if (
                to_skip.command == binding.command
                and to_skip.filter == binding.filter
                and to_skip.keys == binding.keys
            ):
                skip_this_one = True
                break
        if skip_this_one:
            continue
        add_binding(kb, binding)

    def get_input_mode(self):
        app = get_app()
        app.ttimeoutlen = shell.ttimeoutlen
        app.timeoutlen = shell.timeoutlen

        return self._input_mode

    def set_input_mode(self, mode):
        shape = {InputMode.NAVIGATION: 2, InputMode.REPLACE: 4}.get(mode, 6)
        cursor = "\x1b[{} q".format(shape)

        sys.stdout.write(cursor)
        sys.stdout.flush()

        self._input_mode = mode

    if shell.editing_mode == "vi" and shell.modal_cursor:
        ViState._input_mode = InputMode.INSERT  # type: ignore
        ViState.input_mode = property(get_input_mode, set_input_mode)  # type: ignore

    return kb
```
