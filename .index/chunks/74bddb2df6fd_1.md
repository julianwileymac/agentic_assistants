# Chunk: 74bddb2df6fd_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 75-163
- chunk: 2/33

```
===================================================================


class DummyEvent(NoEvent):
    "Dummy event object used internally by L{ConsoleDebugger}."

    def get_pid(self):
        return self._pid

    def get_tid(self):
        return self._tid

    def get_process(self):
        return self._process

    def get_thread(self):
        return self._thread


# ==============================================================================


class CmdError(Exception):
    """
    Exception raised when a command parsing error occurs.
    Used internally by L{ConsoleDebugger}.
    """


# ==============================================================================


class ConsoleDebugger(Cmd, EventHandler):
    """
    Interactive console debugger.

    @see: L{Debug.interactive}
    """

    # ------------------------------------------------------------------------------
    # Class variables

    # Exception to raise when an error occurs executing a command.
    command_error_exception = CmdError

    # Milliseconds to wait for debug events in the main loop.
    dwMilliseconds = 100

    # History file name.
    history_file = ".winappdbg_history"

    # Confirm before quitting?
    confirm_quit = True

    # Valid plugin name characters.
    valid_plugin_name_chars = "ABCDEFGHIJKLMNOPQRSTUVWXY" "abcdefghijklmnopqrstuvwxy" "012345678" "_"

    # Names of the registers.
    segment_names = ("cs", "ds", "es", "fs", "gs")

    register_alias_64_to_32 = {
        "eax": "Rax",
        "ebx": "Rbx",
        "ecx": "Rcx",
        "edx": "Rdx",
        "eip": "Rip",
        "ebp": "Rbp",
        "esp": "Rsp",
        "esi": "Rsi",
        "edi": "Rdi",
    }
    register_alias_64_to_16 = {"ax": "Rax", "bx": "Rbx", "cx": "Rcx", "dx": "Rdx"}
    register_alias_64_to_8_low = {"al": "Rax", "bl": "Rbx", "cl": "Rcx", "dl": "Rdx"}
    register_alias_64_to_8_high = {"ah": "Rax", "bh": "Rbx", "ch": "Rcx", "dh": "Rdx"}
    register_alias_32_to_16 = {"ax": "Eax", "bx": "Ebx", "cx": "Ecx", "dx": "Edx"}
    register_alias_32_to_8_low = {"al": "Eax", "bl": "Ebx", "cl": "Ecx", "dl": "Edx"}
    register_alias_32_to_8_high = {"ah": "Eax", "bh": "Ebx", "ch": "Ecx", "dh": "Edx"}

    register_aliases_full_32 = list(segment_names)
    register_aliases_full_32.extend(compat.iterkeys(register_alias_32_to_16))
    register_aliases_full_32.extend(compat.iterkeys(register_alias_32_to_8_low))
    register_aliases_full_32.extend(compat.iterkeys(register_alias_32_to_8_high))
    register_aliases_full_32 = tuple(register_aliases_full_32)

    register_aliases_full_64 = list(segment_names)
    register_aliases_full_64.extend(compat.iterkeys(register_alias_64_to_32))
    register_aliases_full_64.extend(compat.iterkeys(register_alias_64_to_16))
    register_aliases_full_64.extend(compat.iterkeys(register_alias_64_to_8_low))
```
