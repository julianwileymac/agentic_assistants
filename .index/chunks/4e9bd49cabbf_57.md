# Chunk: 4e9bd49cabbf_57

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 4280-4353
- chunk: 58/64

```
ss of buffer to watch.

        @type  size: int
        @param size: Size in bytes of buffer to watch.

        @type  action: function
        @param action: (Optional) Action callback function.

            See L{define_page_breakpoint} for more details.

        @type  bOneShot: bool
        @param bOneShot:
            C{True} to set a one-shot breakpoint,
            C{False} to set a normal breakpoint.
        """

        # Check the size isn't zero or negative.
        if size < 1:
            raise ValueError("Bad size for buffer watch: %r" % size)

        # Create the buffer watch identifier.
        bw = BufferWatch(pid, address, address + size, action, bOneShot)

        # Get the base address and size in pages required for this buffer.
        base = MemoryAddresses.align_address_to_page_start(address)
        limit = MemoryAddresses.align_address_to_page_end(address + size)
        pages = MemoryAddresses.get_buffer_size_in_pages(address, size)

        try:
            # For each page:
            #  + if a page breakpoint exists reuse it
            #  + if it doesn't exist define it

            bset = set()  # all breakpoints used
            nset = set()  # newly defined breakpoints
            cset = set()  # condition objects

            page_addr = base
            pageSize = MemoryAddresses.pageSize
            while page_addr < limit:
                # If a breakpoints exists, reuse it.
                if self.has_page_breakpoint(pid, page_addr):
                    bp = self.get_page_breakpoint(pid, page_addr)
                    if bp not in bset:
                        condition = bp.get_condition()
                        if not condition in cset:
                            if not isinstance(condition, _BufferWatchCondition):
                                # this shouldn't happen unless you tinkered
                                # with it or defined your own page breakpoints
                                # manually.
                                msg = "Can't watch buffer at page %s"
                                msg = msg % HexDump.address(page_addr)
                                raise RuntimeError(msg)
                            cset.add(condition)
                        bset.add(bp)

                # If it doesn't, define it.
                else:
                    condition = _BufferWatchCondition()
                    bp = self.define_page_breakpoint(pid, page_addr, 1, condition=condition)
                    bset.add(bp)
                    nset.add(bp)
                    cset.add(condition)

                # Next page.
                page_addr = page_addr + pageSize

            # For each breakpoint, enable it if needed.
            aProcess = self.system.get_process(pid)
            for bp in bset:
                if bp.is_disabled() or bp.is_one_shot():
                    bp.enable(aProcess, None)

```
