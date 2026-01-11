# Chunk: 4e9bd49cabbf_25

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 1963-2038
- chunk: 26/64

```
breakpoints,
        enable_process_breakpoints,
        enable_one_shot_process_breakpoints,
        disable_process_breakpoints,
        erase_process_breakpoints

    @group Breakpoint types:
        BP_TYPE_ANY, BP_TYPE_CODE, BP_TYPE_PAGE, BP_TYPE_HARDWARE
    @group Breakpoint states:
        BP_STATE_DISABLED, BP_STATE_ENABLED, BP_STATE_ONESHOT, BP_STATE_RUNNING
    @group Memory breakpoint trigger flags:
        BP_BREAK_ON_EXECUTION, BP_BREAK_ON_WRITE, BP_BREAK_ON_ACCESS
    @group Memory breakpoint size flags:
        BP_WATCH_BYTE, BP_WATCH_WORD, BP_WATCH_DWORD, BP_WATCH_QWORD

    @type BP_TYPE_ANY: int
    @cvar BP_TYPE_ANY: To get all breakpoints
    @type BP_TYPE_CODE: int
    @cvar BP_TYPE_CODE: To get code breakpoints only
    @type BP_TYPE_PAGE: int
    @cvar BP_TYPE_PAGE: To get page breakpoints only
    @type BP_TYPE_HARDWARE: int
    @cvar BP_TYPE_HARDWARE: To get hardware breakpoints only

    @type BP_STATE_DISABLED: int
    @cvar BP_STATE_DISABLED: Breakpoint is disabled.
    @type BP_STATE_ENABLED: int
    @cvar BP_STATE_ENABLED: Breakpoint is enabled.
    @type BP_STATE_ONESHOT: int
    @cvar BP_STATE_ONESHOT: Breakpoint is enabled for one shot.
    @type BP_STATE_RUNNING: int
    @cvar BP_STATE_RUNNING: Breakpoint is running (recently hit).

    @type BP_BREAK_ON_EXECUTION: int
    @cvar BP_BREAK_ON_EXECUTION: Break on code execution.
    @type BP_BREAK_ON_WRITE: int
    @cvar BP_BREAK_ON_WRITE: Break on memory write.
    @type BP_BREAK_ON_ACCESS: int
    @cvar BP_BREAK_ON_ACCESS: Break on memory read or write.
    """

    # Breakpoint types
    BP_TYPE_ANY = 0  # to get all breakpoints
    BP_TYPE_CODE = 1
    BP_TYPE_PAGE = 2
    BP_TYPE_HARDWARE = 3

    # Breakpoint states
    BP_STATE_DISABLED = Breakpoint.DISABLED
    BP_STATE_ENABLED = Breakpoint.ENABLED
    BP_STATE_ONESHOT = Breakpoint.ONESHOT
    BP_STATE_RUNNING = Breakpoint.RUNNING

    # Memory breakpoint trigger flags
    BP_BREAK_ON_EXECUTION = HardwareBreakpoint.BREAK_ON_EXECUTION
    BP_BREAK_ON_WRITE = HardwareBreakpoint.BREAK_ON_WRITE
    BP_BREAK_ON_ACCESS = HardwareBreakpoint.BREAK_ON_ACCESS

    # Memory breakpoint size flags
    BP_WATCH_BYTE = HardwareBreakpoint.WATCH_BYTE
    BP_WATCH_WORD = HardwareBreakpoint.WATCH_WORD
    BP_WATCH_QWORD = HardwareBreakpoint.WATCH_QWORD
    BP_WATCH_DWORD = HardwareBreakpoint.WATCH_DWORD

    def __init__(self):
        self.__codeBP = dict()  # (pid, address) -> CodeBreakpoint
        self.__pageBP = dict()  # (pid, address) -> PageBreakpoint
        self.__hardwareBP = dict()  # tid -> [ HardwareBreakpoint ]
        self.__runningBP = dict()  # tid -> set( Breakpoint )
        self.__tracing = set()  # set( tid )
        self.__deferredBP = dict()  # pid -> label -> (action, oneshot)

    # ------------------------------------------------------------------------------

    # This operates on the dictionary of running breakpoints.
```
