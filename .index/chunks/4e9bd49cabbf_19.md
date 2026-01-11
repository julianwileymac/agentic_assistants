# Chunk: 4e9bd49cabbf_19

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 1488-1559
- chunk: 20/64

```
tion" " for the %s architecture"
                    ) % win32.arch
                    raise NotImplementedError(msg)

        if reg_int_sig:

            class RegisterArguments(ctypes.Structure):
                _fields_ = reg_int_sig
        else:
            RegisterArguments = None
        if reg_float_sig:

            class FloatArguments(ctypes.Structure):
                _fields_ = reg_float_sig
        else:
            FloatArguments = None
        if stack_sig:

            class StackArguments(ctypes.Structure):
                _fields_ = stack_sig
        else:
            StackArguments = None

        return (len(signature), RegisterArguments, FloatArguments, StackArguments)

    def _get_return_address(self, aProcess, aThread):
        return aProcess.read_pointer(aThread.get_sp())

    def _get_function_arguments(self, aProcess, aThread):
        if self._signature:
            (args_count, RegisterArguments, FloatArguments, StackArguments) = self._signature
            arguments = {}
            if StackArguments:
                address = aThread.get_sp() + win32.sizeof(win32.LPVOID)
                stack_struct = aProcess.read_structure(address, StackArguments)
                stack_args = dict([(name, stack_struct.__getattribute__(name)) for (name, type) in stack_struct._fields_])
                arguments.update(stack_args)
            flags = 0
            if RegisterArguments:
                flags = flags | win32.CONTEXT_INTEGER
            if FloatArguments:
                flags = flags | win32.CONTEXT_MMX_REGISTERS
            if flags:
                ctx = aThread.get_context(flags)
                if RegisterArguments:
                    buffer = (win32.QWORD * 4)(ctx["Rcx"], ctx["Rdx"], ctx["R8"], ctx["R9"])
                    reg_args = self._get_arguments_from_buffer(buffer, RegisterArguments)
                    arguments.update(reg_args)
                if FloatArguments:
                    buffer = (win32.M128A * 4)(ctx["XMM0"], ctx["XMM1"], ctx["XMM2"], ctx["XMM3"])
                    float_args = self._get_arguments_from_buffer(buffer, FloatArguments)
                    arguments.update(float_args)
            params = tuple([arguments["arg_%d" % i] for i in compat.xrange(args_count)])
        else:
            params = ()
        return params

    def _get_arguments_from_buffer(self, buffer, structure):
        b_ptr = ctypes.pointer(buffer)
        v_ptr = ctypes.cast(b_ptr, ctypes.c_void_p)
        s_ptr = ctypes.cast(v_ptr, ctypes.POINTER(structure))
        struct = s_ptr.contents
        return dict([(name, struct.__getattribute__(name)) for (name, type) in struct._fields_])

    def _get_return_value(self, aThread):
        ctx = aThread.get_context(win32.CONTEXT_INTEGER)
        return ctx["Rax"]


# ------------------------------------------------------------------------------

```
