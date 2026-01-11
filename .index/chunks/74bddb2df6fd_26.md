# Chunk: 74bddb2df6fd_26

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 1833-1916
- chunk: 27/33

```
]
            next_address = last_code[0] + last_code[1]
            next_address = HexOutput.integer(next_address)
            self.default_disasm_target = next_address
            print("%s:" % label)
            # #            print(CrashDump.dump_code(code))
            for line in code:
                print(CrashDump.dump_code_line(line, bShowDump=False))

    do_u = do_disassemble

    def do_search(self, arg):
        """
        [~process] s [address-address] <search string>
        [~process] search [address-address] <search string>
        """
        token_list = self.split_tokens(arg, 1, 3)
        pid, tid = self.get_process_and_thread_ids_from_prefix()
        process = self.get_process(pid)
        if len(token_list) == 1:
            pattern = token_list[0]
            minAddr = None
            maxAddr = None
        else:
            pattern = token_list[-1]
            addr, size = self.input_address_range(token_list[:-1], pid, tid)
            minAddr = addr
            maxAddr = addr + size
        iter = process.search_bytes(pattern)
        if process.get_bits() == 32:
            addr_width = 8
        else:
            addr_width = 16
        # TODO: need a prettier output here!
        for addr in iter:
            print(HexDump.address(addr, addr_width))

    do_s = do_search

    def do_searchhex(self, arg):
        """
        [~process] sh [address-address] <hexadecimal pattern>
        [~process] searchhex [address-address] <hexadecimal pattern>
        """
        token_list = self.split_tokens(arg, 1, 3)
        pid, tid = self.get_process_and_thread_ids_from_prefix()
        process = self.get_process(pid)
        if len(token_list) == 1:
            pattern = token_list[0]
            minAddr = None
            maxAddr = None
        else:
            pattern = token_list[-1]
            addr, size = self.input_address_range(token_list[:-1], pid, tid)
            minAddr = addr
            maxAddr = addr + size
        iter = process.search_hexa(pattern)
        if process.get_bits() == 32:
            addr_width = 8
        else:
            addr_width = 16
        for addr, bytes in iter:
            print(
                HexDump.hexblock(bytes, addr, addr_width),
            )

    do_sh = do_searchhex

    # #    def do_strings(self, arg):
    # #        """
    # #        [~process] strings - extract ASCII strings from memory
    # #        """
    # #        if arg:
    # #            raise CmdError("too many arguments")
    # #        pid, tid   = self.get_process_and_thread_ids_from_prefix()
    # #        process    = self.get_process(pid)
    # #        for addr, size, data in process.strings():
    # #            print("%s: %r" % (HexDump.address(addr), data)

    def do_d(self, arg):
        """
        [~thread] d <register> - show memory contents
        [~thread] d <register-register> - show memory contents
```
