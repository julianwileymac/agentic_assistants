# Chunk: 4e9bd49cabbf_20

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 1550-1628
- chunk: 21/64

```
ict([(name, struct.__getattribute__(name)) for (name, type) in struct._fields_])

    def _get_return_value(self, aThread):
        ctx = aThread.get_context(win32.CONTEXT_INTEGER)
        return ctx["Rax"]


# ------------------------------------------------------------------------------

# This class acts as a factory of Hook objects, one per target process.
# Said objects are deleted by the unhook() method.


class ApiHook(object):
    """
    Used by L{EventHandler}.

    This class acts as an action callback for code breakpoints set at the
    beginning of a function. It automatically retrieves the parameters from
    the stack, sets a breakpoint at the return address and retrieves the
    return value from the function call.

    @see: L{EventHandler.apiHooks}

    @type modName: str
    @ivar modName: Module name.

    @type procName: str
    @ivar procName: Procedure name.
    """

    def __init__(self, eventHandler, modName, procName, paramCount=None, signature=None):
        """
        @type  eventHandler: L{EventHandler}
        @param eventHandler: Event handler instance. This is where the hook
            callbacks are to be defined (see below).

        @type  modName: str
        @param modName: Module name.

        @type  procName: str
        @param procName: Procedure name.
            The pre and post callbacks will be deduced from it.

            For example, if the procedure is "LoadLibraryEx" the callback
            routines will be "pre_LoadLibraryEx" and "post_LoadLibraryEx".

            The signature for the callbacks should be something like this::

                def pre_LoadLibraryEx(self, event, ra, lpFilename, hFile, dwFlags):

                    # return address
                    ra = params[0]

                    # function arguments start from here...
                    szFilename = event.get_process().peek_string(lpFilename)

                    # (...)

                def post_LoadLibraryEx(self, event, return_value):

                    # (...)

            Note that all pointer types are treated like void pointers, so your
            callback won't get the string or structure pointed to by it, but
            the remote memory address instead. This is so to prevent the ctypes
            library from being "too helpful" and trying to dereference the
            pointer. To get the actual data being pointed to, use one of the
            L{Process.read} methods.

        @type  paramCount: int
        @param paramCount:
            (Optional) Number of parameters for the C{preCB} callback,
            not counting the return address. Parameters are read from
            the stack and assumed to be DWORDs in 32 bits and QWORDs in 64.

            This is a faster way to pull stack parameters in 32 bits, but in 64
            bits (or with some odd APIs in 32 bits) it won't be useful, since
```
