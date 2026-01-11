# Chunk: aa04dfa46dea_1

- source: `.venv-lab/Lib/site-packages/prompt_toolkit/application/run_in_terminal.py`
- lines: 84-118
- chunk: 2/2

```
f

    # Wait for all CPRs to arrive. We don't want to detach the input until
    # all cursor position responses have been arrived. Otherwise, the tty
    # will echo its input and can show stuff like ^[[39;1R.
    if app.output.responds_to_cpr:
        await app.renderer.wait_for_cpr_responses()

    # Draw interface in 'done' state, or erase.
    if render_cli_done:
        app._redraw(render_as_done=True)
    else:
        app.renderer.erase()

    # Disable rendering.
    app._running_in_terminal = True

    # Detach input.
    try:
        with app.input.detach():
            with app.input.cooked_mode():
                yield
    finally:
        # Redraw interface again.
        try:
            app._running_in_terminal = False
            app.renderer.reset()
            app._request_absolute_cursor_position()
            app._redraw()
        finally:
            # (Check for `.done()`, because it can be that this future was
            # cancelled.)
            if not new_run_in_terminal_f.done():
                new_run_in_terminal_f.set_result(None)
```
