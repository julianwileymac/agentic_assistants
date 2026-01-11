# Chunk: 4e9bd49cabbf_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 75-172
- chunk: 2/64

```
    """
    This warning is issued when a non-fatal error occurs that's related to
    breakpoints.
    """


class BreakpointCallbackWarning(RuntimeWarning):
    """
    This warning is issued when an uncaught exception was raised by a
    breakpoint's user-defined callback.
    """


# ==============================================================================


class Breakpoint(object):
    """
    Base class for breakpoints.
    Here's the breakpoints state machine.

    @see: L{CodeBreakpoint}, L{PageBreakpoint}, L{HardwareBreakpoint}

    @group Breakpoint states:
        DISABLED, ENABLED, ONESHOT, RUNNING
    @group State machine:
        hit, disable, enable, one_shot, running,
        is_disabled, is_enabled, is_one_shot, is_running,
        get_state, get_state_name
    @group Information:
        get_address, get_size, get_span, is_here
    @group Conditional breakpoints:
        is_conditional, is_unconditional,
        get_condition, set_condition, eval_condition
    @group Automatic breakpoints:
        is_automatic, is_interactive,
        get_action, set_action, run_action

    @cvar DISABLED: I{Disabled} S{->} Enabled, OneShot
    @cvar ENABLED:  I{Enabled}  S{->} I{Running}, Disabled
    @cvar ONESHOT:  I{OneShot}  S{->} I{Disabled}
    @cvar RUNNING:  I{Running}  S{->} I{Enabled}, Disabled

    @type DISABLED: int
    @type ENABLED:  int
    @type ONESHOT:  int
    @type RUNNING:  int

    @type stateNames: dict E{lb} int S{->} str E{rb}
    @cvar stateNames: User-friendly names for each breakpoint state.

    @type typeName: str
    @cvar typeName: User friendly breakpoint type string.
    """

    # I don't think transitions Enabled <-> OneShot should be allowed... plus
    #  it would require special handling to avoid setting the same bp twice

    DISABLED = 0
    ENABLED = 1
    ONESHOT = 2
    RUNNING = 3

    typeName = "breakpoint"

    stateNames = {
        DISABLED: "disabled",
        ENABLED: "enabled",
        ONESHOT: "one shot",
        RUNNING: "running",
    }

    def __init__(self, address, size=1, condition=True, action=None):
        """
        Breakpoint object.

        @type  address: int
        @param address: Memory address for breakpoint.

        @type  size: int
        @param size: Size of breakpoint in bytes (defaults to 1).

        @type  condition: function
        @param condition: (Optional) Condition callback function.

            The callback signature is::

                def condition_callback(event):
                    return True     # returns True or False

            Where B{event} is an L{Event} object,
            and the return value is a boolean
            (C{True} to dispatch the event, C{False} otherwise).

        @type  action: function
        @param action: (Optional) Action callback function.
            If specified, the event is handled by this callback instead of
```
