# Chunk: 4e9bd49cabbf_60

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 4476-4570
- chunk: 61/64

```
  @param size: Size in bytes of buffer to watch.

        @type  action: function
        @param action: (Optional) Action callback function.

            See L{define_page_breakpoint} for more details.

        @rtype:  L{BufferWatch}
        @return: Buffer watch identifier.
        """
        self.__set_buffer_watch(pid, address, size, action, False)

    def stalk_buffer(self, pid, address, size, action=None):
        """
        Sets a one-shot page breakpoint and notifies
        when the given buffer is accessed.

        @see: L{dont_watch_variable}

        @type  pid: int
        @param pid: Process global ID.

        @type  address: int
        @param address: Memory address of buffer to watch.

        @type  size: int
        @param size: Size in bytes of buffer to watch.

        @type  action: function
        @param action: (Optional) Action callback function.

            See L{define_page_breakpoint} for more details.

        @rtype:  L{BufferWatch}
        @return: Buffer watch identifier.
        """
        self.__set_buffer_watch(pid, address, size, action, True)

    def dont_watch_buffer(self, bw, *argv, **argd):
        """
        Clears a page breakpoint set by L{watch_buffer}.

        @type  bw: L{BufferWatch}
        @param bw:
            Buffer watch identifier returned by L{watch_buffer}.
        """

        # The sane way to do it.
        if not (argv or argd):
            self.__clear_buffer_watch(bw)

        # Backwards compatibility with WinAppDbg 1.4.
        else:
            argv = list(argv)
            argv.insert(0, bw)
            if "pid" in argd:
                argv.insert(0, argd.pop("pid"))
            if "address" in argd:
                argv.insert(1, argd.pop("address"))
            if "size" in argd:
                argv.insert(2, argd.pop("size"))
            if argd:
                raise TypeError("Wrong arguments for dont_watch_buffer()")
            try:
                pid, address, size = argv
            except ValueError:
                raise TypeError("Wrong arguments for dont_watch_buffer()")
            self.__clear_buffer_watch_old_method(pid, address, size)

    def dont_stalk_buffer(self, bw, *argv, **argd):
        """
        Clears a page breakpoint set by L{stalk_buffer}.

        @type  bw: L{BufferWatch}
        @param bw:
            Buffer watch identifier returned by L{stalk_buffer}.
        """
        self.dont_watch_buffer(bw, *argv, **argd)

    # ------------------------------------------------------------------------------

    # Tracing

    # XXX TODO
    # Add "action" parameter to tracing mode

    def __start_tracing(self, thread):
        """
        @type  thread: L{Thread}
        @param thread: Thread to start tracing.
        """
        tid = thread.get_tid()
        if not tid in self.__tracing:
            thread.set_tf()
```
