# Chunk: 4e9bd49cabbf_14

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 1099-1175
- chunk: 15/64

```
 and assumed to be DWORDs in 32 bits and QWORDs in 64.

            This is a faster way to pull stack parameters in 32 bits, but in 64
            bits (or with some odd APIs in 32 bits) it won't be useful, since
            not all arguments to the hooked function will be of the same size.

            For a more reliable and cross-platform way of hooking use the
            C{signature} argument instead.

        @type  signature: tuple
        @param signature:
            (Optional) Tuple of C{ctypes} data types that constitute the
            hooked function signature. When the function is called, this will
            be used to parse the arguments from the stack. Overrides the
            C{paramCount} argument.

        @type  arch: str
        @param arch: (Optional) Target architecture. Defaults to the current
            architecture. See: L{win32.arch}
        """
        self.__preCB = preCB
        self.__postCB = postCB
        self.__paramStack = dict()  # tid -> list of tuple( arg, arg, arg... )

        self._paramCount = paramCount

        if win32.arch != win32.ARCH_I386:
            self.useHardwareBreakpoints = False

        if win32.bits == 64 and paramCount and not signature:
            signature = (win32.QWORD,) * paramCount

        if signature:
            self._signature = self._calc_signature(signature)
        else:
            self._signature = None

    def _cast_signature_pointers_to_void(self, signature):
        c_void_p = ctypes.c_void_p
        c_char_p = ctypes.c_char_p
        c_wchar_p = ctypes.c_wchar_p
        _Pointer = ctypes._Pointer
        cast = ctypes.cast
        for i in compat.xrange(len(signature)):
            t = signature[i]
            if t is not c_void_p and (issubclass(t, _Pointer) or t in [c_char_p, c_wchar_p]):
                signature[i] = cast(t, c_void_p)

    def _calc_signature(self, signature):
        raise NotImplementedError("Hook signatures are not supported for architecture: %s" % win32.arch)

    def _get_return_address(self, aProcess, aThread):
        return None

    def _get_function_arguments(self, aProcess, aThread):
        if self._signature or self._paramCount:
            raise NotImplementedError("Hook signatures are not supported for architecture: %s" % win32.arch)
        return ()

    def _get_return_value(self, aThread):
        return None

    # By using break_at() to set a process-wide breakpoint on the function's
    # return address, we might hit a race condition when more than one thread
    # is being debugged.
    #
    # Hardware breakpoints should be used instead. But since a thread can run
    # out of those, we need to fall back to this method when needed.

    def __call__(self, event):
        """
        Handles the breakpoint event on entry of the function.

        @type  event: L{ExceptionEvent}
        @param event: Breakpoint hit event.

```
