# Chunk: 74bddb2df6fd_29

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 2031-2116
- chunk: 30/33

```
s = thread.get_process()
                    module = process.get_module_at_address(value)
                    if module:
                        label = module.get_label_at_address(value)
                except RuntimeError:
                    label = None
                reg = arg.upper()
                val = HexDump.address(value)
                if label:
                    print("%s: %s (%s)" % (reg, val, label))
                else:
                    print("%s: %s" % (reg, val))

    do_r = do_register

    def do_eb(self, arg):
        """
        [~process] eb <address> <data> - write the data to the specified address
        """
        # TODO
        # data parameter should be optional, use a child Cmd here
        pid = self.get_process_id_from_prefix()
        token_list = self.split_tokens(arg, 2)
        address = self.input_address(token_list[0], pid)
        data = HexInput.hexadecimal(" ".join(token_list[1:]))
        self.write_memory(address, data, pid)

    # XXX TODO
    # add ew, ed and eq here

    def do_find(self, arg):
        """
        [~process] f <string> - find the string in the process memory
        [~process] find <string> - find the string in the process memory
        """
        if not arg:
            raise CmdError("missing parameter: string")
        process = self.get_process_from_prefix()
        self.find_in_memory(arg, process)

    do_f = do_find

    def do_memory(self, arg):
        """
        [~process] m - show the process memory map
        [~process] memory - show the process memory map
        """
        if arg:  # TODO: take min and max addresses
            raise CmdError("too many arguments")
        process = self.get_process_from_prefix()
        try:
            memoryMap = process.get_memory_map()
            mappedFilenames = process.get_mapped_filenames()
            print("")
            print(CrashDump.dump_memory_map(memoryMap, mappedFilenames))
        except WindowsError:
            msg = "can't get memory information for process (%d)"
            raise CmdError(msg % process.get_pid())

    do_m = do_memory

    # ------------------------------------------------------------------------------
    # Event handling

    # TODO
    # * add configurable stop/don't stop behavior on events and exceptions

    # Stop for all events, unless stated otherwise.
    def event(self, event):
        self.print_event(event)
        self.prompt_user()

    # Stop for all exceptions, unless stated otherwise.
    def exception(self, event):
        self.print_exception(event)
        self.prompt_user()

    # Stop for breakpoint exceptions.
    def breakpoint(self, event):
        if hasattr(event, "breakpoint") and event.breakpoint:
            self.print_breakpoint_location(event)
        else:
            self.print_exception(event)
        self.prompt_user()

```
