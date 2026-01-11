# Chunk: 4e9bd49cabbf_59

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 4412-4486
- chunk: 60/64

```
) == 0:
                        try:
                            self.erase_page_breakpoint(pid, bp.get_address())
                        except WindowsError:
                            pass
            page_addr = page_addr + pageSize

    def __clear_buffer_watch(self, bw):
        """
        Used by L{dont_watch_buffer} and L{dont_stalk_buffer}.

        @type  bw: L{BufferWatch}
        @param bw: Buffer watch identifier.
        """

        # Get the PID and the start and end addresses of the buffer.
        pid = bw.pid
        start = bw.start
        end = bw.end

        # Get the base address and size in pages required for the buffer.
        base = MemoryAddresses.align_address_to_page_start(start)
        limit = MemoryAddresses.align_address_to_page_end(end)
        pages = MemoryAddresses.get_buffer_size_in_pages(start, end - start)

        # For each page, get the breakpoint and it's condition object.
        # For each condition, remove the buffer.
        # For each breakpoint, if no buffers are on watch, erase it.
        cset = set()  # condition objects
        page_addr = base
        pageSize = MemoryAddresses.pageSize
        while page_addr < limit:
            if self.has_page_breakpoint(pid, page_addr):
                bp = self.get_page_breakpoint(pid, page_addr)
                condition = bp.get_condition()
                if condition not in cset:
                    if not isinstance(condition, _BufferWatchCondition):
                        # this shouldn't happen unless you tinkered with it
                        # or defined your own page breakpoints manually.
                        continue
                    cset.add(condition)
                    condition.remove(bw)
                    if condition.count() == 0:
                        try:
                            self.erase_page_breakpoint(pid, bp.get_address())
                        except WindowsError:
                            msg = "Cannot remove page breakpoint at address %s"
                            msg = msg % HexDump.address(bp.get_address())
                            warnings.warn(msg, BreakpointWarning)
            page_addr = page_addr + pageSize

    def watch_buffer(self, pid, address, size, action=None):
        """
        Sets a page breakpoint and notifies when the given buffer is accessed.

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
```
