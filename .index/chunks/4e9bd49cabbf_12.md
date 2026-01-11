# Chunk: 4e9bd49cabbf_12

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 968-1040
- chunk: 13/64

```
f.__clear_bp(aThread)
        super(HardwareBreakpoint, self).running(aProcess, aThread)
        aThread.set_tf()


# ==============================================================================

# XXX FIXME
#
# The implementation of function hooks is very simple. A breakpoint is set at
# the entry point. Each time it's hit the "pre" callback is executed. If a
# "post" callback was defined, a one-shot breakpoint is set at the return
# address - and when that breakpoint hits, the "post" callback is executed.
#
# Functions hooks, as they are implemented now, don't work correctly for
# recursive functions. The problem is we don't know when to remove the
# breakpoint at the return address. Also there could be more than one return
# address.
#
# One possible solution would involve a dictionary of lists, where the key
# would be the thread ID and the value a stack of return addresses. But we
# still don't know what to do if the "wrong" return address is hit for some
# reason (maybe check the stack pointer?). Or if both a code and a hardware
# breakpoint are hit simultaneously.
#
# For now, the workaround for the user is to set only the "pre" callback for
# functions that are known to be recursive.
#
# If an exception is thrown by a hooked function and caught by one of it's
# parent functions, the "post" callback won't be called and weird stuff may
# happen. A possible solution is to put a breakpoint in the system call that
# unwinds the stack, to detect this case and remove the "post" breakpoint.
#
# Hooks may also behave oddly if the return address is overwritten by a buffer
# overflow bug (this is similar to the exception problem). But it's probably a
# minor issue since when you're fuzzing a function for overflows you're usually
# not interested in the return value anyway.

# TODO: an API to modify the hooked function's arguments


class Hook(object):
    """
    Factory class to produce hook objects. Used by L{Debug.hook_function} and
    L{Debug.stalk_function}.

    When you try to instance this class, one of the architecture specific
    implementations is returned instead.

    Instances act as an action callback for code breakpoints set at the
    beginning of a function. It automatically retrieves the parameters from
    the stack, sets a breakpoint at the return address and retrieves the
    return value from the function call.

    @see: L{_Hook_i386}, L{_Hook_amd64}

    @type useHardwareBreakpoints: bool
    @cvar useHardwareBreakpoints: C{True} to try to use hardware breakpoints,
        C{False} otherwise.
    """

    # This is a factory class that returns
    # the architecture specific implementation.
    def __new__(cls, *argv, **argd):
        try:
            arch = argd["arch"]
            del argd["arch"]
        except KeyError:
            try:
                arch = argv[4]
                argv = argv[:4] + argv[5:]
            except IndexError:
```
