# Chunk: 74bddb2df6fd_2

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 157-260
- chunk: 3/33

```
_32)

    register_aliases_full_64 = list(segment_names)
    register_aliases_full_64.extend(compat.iterkeys(register_alias_64_to_32))
    register_aliases_full_64.extend(compat.iterkeys(register_alias_64_to_16))
    register_aliases_full_64.extend(compat.iterkeys(register_alias_64_to_8_low))
    register_aliases_full_64.extend(compat.iterkeys(register_alias_64_to_8_high))
    register_aliases_full_64 = tuple(register_aliases_full_64)

    # Names of the control flow instructions.
    jump_instructions = (
        "jmp",
        "jecxz",
        "jcxz",
        "ja",
        "jnbe",
        "jae",
        "jnb",
        "jb",
        "jnae",
        "jbe",
        "jna",
        "jc",
        "je",
        "jz",
        "jnc",
        "jne",
        "jnz",
        "jnp",
        "jpo",
        "jp",
        "jpe",
        "jg",
        "jnle",
        "jge",
        "jnl",
        "jl",
        "jnge",
        "jle",
        "jng",
        "jno",
        "jns",
        "jo",
        "js",
    )
    call_instructions = ("call", "ret", "retn")
    loop_instructions = ("loop", "loopz", "loopnz", "loope", "loopne")
    control_flow_instructions = call_instructions + loop_instructions + jump_instructions

    # ------------------------------------------------------------------------------
    # Instance variables

    def __init__(self):
        """
        Interactive console debugger.

        @see: L{Debug.interactive}
        """
        Cmd.__init__(self)
        EventHandler.__init__(self)

        # Quit the debugger when True.
        self.debuggerExit = False

        # Full path to the history file.
        self.history_file_full_path = None

        # Last executed command.
        self.__lastcmd = ""

    # ------------------------------------------------------------------------------
    # Debugger

    # Use this Debug object.
    def start_using_debugger(self, debug):
        # Clear the previous Debug object.
        self.stop_using_debugger()

        # Keep the Debug object.
        self.debug = debug

        # Set ourselves as the event handler for the debugger.
        self.prevHandler = debug.set_event_handler(self)

    # Stop using the Debug object given by start_using_debugger().
    # Circular references must be removed, or the destructors never get called.
    def stop_using_debugger(self):
        if hasattr(self, "debug"):
            debug = self.debug
            debug.set_event_handler(self.prevHandler)
            del self.prevHandler
            del self.debug
            return debug
        return None

    # Destroy the Debug object.
    def destroy_debugger(self, autodetach=True):
        debug = self.stop_using_debugger()
        if debug is not None:
            if not autodetach:
                debug.kill_all(bIgnoreExceptions=True)
                debug.lastEvent = None
            debug.stop()
```
