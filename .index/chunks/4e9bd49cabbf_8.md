# Chunk: 4e9bd49cabbf_8

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 639-720
- chunk: 9/64

```
the breakpoint.
# * If the page permissions were modified after the breakpoint was enabled,
#   no change should be done on them when disabling the breakpoint. For this
#   we need to remember the original page permissions instead of blindly
#   setting and clearing the guard page bit on them.
# * Some pages seem to be "magic" and resist all attempts at changing their
#   protect bits (for example the pages where the PEB and TEB reside). Maybe
#   a more descriptive error message could be shown in this case.


class PageBreakpoint(Breakpoint):
    """
    Page access breakpoint (using guard pages).

    @see: L{Debug.watch_buffer}

    @group Information:
        get_size_in_pages
    """

    typeName = "page breakpoint"

    # ------------------------------------------------------------------------------

    def __init__(self, address, pages=1, condition=True, action=None):
        """
        Page breakpoint object.

        @see: L{Breakpoint.__init__}

        @type  address: int
        @param address: Memory address for breakpoint.

        @type  pages: int
        @param address: Size of breakpoint in pages.

        @type  condition: function
        @param condition: (Optional) Condition callback function.

        @type  action: function
        @param action: (Optional) Action callback function.
        """
        Breakpoint.__init__(self, address, pages * MemoryAddresses.pageSize, condition, action)
        ##        if (address & 0x00000FFF) != 0:
        floordiv_align = long(address) // long(MemoryAddresses.pageSize)
        truediv_align = float(address) / float(MemoryAddresses.pageSize)
        if floordiv_align != truediv_align:
            msg = "Address of page breakpoint " "must be aligned to a page size boundary " "(value %s received)" % HexDump.address(address)
            raise ValueError(msg)

    def get_size_in_pages(self):
        """
        @rtype:  int
        @return: The size in pages of the breakpoint.
        """
        # The size is always a multiple of the page size.
        return self.get_size() // MemoryAddresses.pageSize

    def __set_bp(self, aProcess):
        """
        Sets the target pages as guard pages.

        @type  aProcess: L{Process}
        @param aProcess: Process object.
        """
        lpAddress = self.get_address()
        dwSize = self.get_size()
        flNewProtect = aProcess.mquery(lpAddress).Protect
        flNewProtect = flNewProtect | win32.PAGE_GUARD
        aProcess.mprotect(lpAddress, dwSize, flNewProtect)

    def __clear_bp(self, aProcess):
        """
        Restores the original permissions of the target pages.

        @type  aProcess: L{Process}
        @param aProcess: Process object.
        """
        lpAddress = self.get_address()
        flNewProtect = aProcess.mquery(lpAddress).Protect
        flNewProtect = flNewProtect & (0xFFFFFFFF ^ win32.PAGE_GUARD)  # DWORD
```
