# Chunk: 4e9bd49cabbf_17

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 1313-1419
- chunk: 18/64

```
he hooked function
        from this thread.

        @type  tid: int
        @param tid: Thread global ID.

        @type  params: tuple( arg, arg, arg... )
        @param params: Tuple of arguments.
        """
        stack = self.__paramStack.get(tid, [])
        stack.append(params)
        self.__paramStack[tid] = stack

    def __pop_params(self, tid):
        """
        Forgets the arguments tuple for the last call to the hooked function
        from this thread.

        @type  tid: int
        @param tid: Thread global ID.
        """
        stack = self.__paramStack[tid]
        stack.pop()
        if not stack:
            del self.__paramStack[tid]

    def get_params(self, tid):
        """
        Returns the parameters found in the stack when the hooked function
        was last called by this thread.

        @type  tid: int
        @param tid: Thread global ID.

        @rtype:  tuple( arg, arg, arg... )
        @return: Tuple of arguments.
        """
        try:
            params = self.get_params_stack(tid)[-1]
        except IndexError:
            msg = "Hooked function called from thread %d already returned"
            raise IndexError(msg % tid)
        return params

    def get_params_stack(self, tid):
        """
        Returns the parameters found in the stack each time the hooked function
        was called by this thread and hasn't returned yet.

        @type  tid: int
        @param tid: Thread global ID.

        @rtype:  list of tuple( arg, arg, arg... )
        @return: List of argument tuples.
        """
        try:
            stack = self.__paramStack[tid]
        except KeyError:
            msg = "Hooked function was not called from thread %d"
            raise KeyError(msg % tid)
        return stack

    def hook(self, debug, pid, address):
        """
        Installs the function hook at a given process and address.

        @see: L{unhook}

        @warning: Do not call from an function hook callback.

        @type  debug: L{Debug}
        @param debug: Debug object.

        @type  pid: int
        @param pid: Process ID.

        @type  address: int
        @param address: Function address.
        """
        return debug.break_at(pid, address, self)

    def unhook(self, debug, pid, address):
        """
        Removes the function hook at a given process and address.

        @see: L{hook}

        @warning: Do not call from an function hook callback.

        @type  debug: L{Debug}
        @param debug: Debug object.

        @type  pid: int
        @param pid: Process ID.

        @type  address: int
        @param address: Function address.
        """
        return debug.dont_break_at(pid, address)


class _Hook_i386(Hook):
    """
    Implementation details for L{Hook} on the L{win32.ARCH_I386} architecture.
    """

```
