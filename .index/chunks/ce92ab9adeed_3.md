# Chunk: ce92ab9adeed_3

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_console.py`
- lines: 205-266
- chunk: 4/4

```
interactive console.
    interactive console should have been initialized by this time
    :rtype: DebugConsole
    """
    if InteractiveConsoleCache.thread_id == thread_id and InteractiveConsoleCache.frame_id == frame_id:
        return InteractiveConsoleCache.interactive_console_instance

    InteractiveConsoleCache.interactive_console_instance = DebugConsole()
    InteractiveConsoleCache.thread_id = thread_id
    InteractiveConsoleCache.frame_id = frame_id

    console_stacktrace = traceback.extract_stack(frame, limit=1)
    if console_stacktrace:
        current_context = console_stacktrace[0]  # top entry from stacktrace
        context_message = 'File "%s", line %s, in %s' % (current_context[0], current_context[1], current_context[2])
        console_message.add_console_message(CONSOLE_OUTPUT, "[Current context]: %s" % (context_message,))
    return InteractiveConsoleCache.interactive_console_instance


def clear_interactive_console():
    InteractiveConsoleCache.thread_id = None
    InteractiveConsoleCache.frame_id = None
    InteractiveConsoleCache.interactive_console_instance = None


def execute_console_command(frame, thread_id, frame_id, line, buffer_output=True):
    """fetch an interactive console instance from the cache and
    push the received command to the console.

    create and return an instance of console_message
    """
    console_message = ConsoleMessage()

    interpreter = get_interactive_console(thread_id, frame_id, frame, console_message)
    more, output_messages, error_messages = interpreter.push(line, frame, buffer_output)
    console_message.update_more(more)

    for message in output_messages:
        console_message.add_console_message(CONSOLE_OUTPUT, message)

    for message in error_messages:
        console_message.add_console_message(CONSOLE_ERROR, message)

    return console_message


def get_description(frame, thread_id, frame_id, expression):
    console_message = ConsoleMessage()
    interpreter = get_interactive_console(thread_id, frame_id, frame, console_message)
    try:
        interpreter.frame = frame
        return interpreter.getDescription(expression)
    finally:
        interpreter.frame = None


def get_completions(frame, act_tok):
    """fetch all completions, create xml for the same
    return the completions xml
    """
    return _pydev_completer.generate_completions_as_xml(frame, act_tok)
```
