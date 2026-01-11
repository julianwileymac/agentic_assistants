# Chunk: 4e9bd49cabbf_18

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 1405-1498
- chunk: 19/64

```

        @param pid: Process ID.

        @type  address: int
        @param address: Function address.
        """
        return debug.dont_break_at(pid, address)


class _Hook_i386(Hook):
    """
    Implementation details for L{Hook} on the L{win32.ARCH_I386} architecture.
    """

    # We don't want to inherit the parent class __new__ method.
    __new__ = object.__new__

    def _calc_signature(self, signature):
        self._cast_signature_pointers_to_void(signature)

        class Arguments(ctypes.Structure):
            _fields_ = [("arg_%s" % i, signature[i]) for i in compat.xrange(len(signature) - 1, -1, -1)]

        return Arguments

    def _get_return_address(self, aProcess, aThread):
        return aProcess.read_pointer(aThread.get_sp())

    def _get_function_arguments(self, aProcess, aThread):
        if self._signature:
            params = aThread.read_stack_structure(self._signature, offset=win32.sizeof(win32.LPVOID))
        elif self._paramCount:
            params = aThread.read_stack_dwords(self._paramCount, offset=win32.sizeof(win32.LPVOID))
        else:
            params = ()
        return params

    def _get_return_value(self, aThread):
        ctx = aThread.get_context(win32.CONTEXT_INTEGER)
        return ctx["Eax"]


class _Hook_amd64(Hook):
    """
    Implementation details for L{Hook} on the L{win32.ARCH_AMD64} architecture.
    """

    # We don't want to inherit the parent class __new__ method.
    __new__ = object.__new__

    # Make a list of floating point types.
    __float_types = (
        ctypes.c_double,
        ctypes.c_float,
    )
    # Long doubles are not supported in old versions of ctypes!
    try:
        __float_types += (ctypes.c_longdouble,)
    except AttributeError:
        pass

    def _calc_signature(self, signature):
        self._cast_signature_pointers_to_void(signature)

        float_types = self.__float_types
        c_sizeof = ctypes.sizeof
        reg_size = c_sizeof(ctypes.c_size_t)

        reg_int_sig = []
        reg_float_sig = []
        stack_sig = []

        for i in compat.xrange(len(signature)):
            arg = signature[i]
            name = "arg_%d" % i
            stack_sig.insert(0, (name, arg))
            if i < 4:
                if type(arg) in float_types:
                    reg_float_sig.append((name, arg))
                elif c_sizeof(arg) <= reg_size:
                    reg_int_sig.append((name, arg))
                else:
                    msg = (
                        "Hook signatures don't support structures" " within the first 4 arguments of a function" " for the %s architecture"
                    ) % win32.arch
                    raise NotImplementedError(msg)

        if reg_int_sig:

            class RegisterArguments(ctypes.Structure):
                _fields_ = reg_int_sig
        else:
            RegisterArguments = None
```
