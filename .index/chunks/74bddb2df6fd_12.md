# Chunk: 74bddb2df6fd_12

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 864-943
- chunk: 13/33

```
w part).
            if register in self.register_alias_8_low:
                register = self.register_alias_8_low[register]
                previous = ctx.get(register) % 0xFFFFFF00
                value = (value & 0x000000FF) | previous

            # Integer 8 bits registers (high part).
            if register in self.register_alias_8_high:
                register = self.register_alias_8_high[register]
                previous = ctx.get(register) % 0xFFFF00FF
                value = ((value & 0x000000FF) << 8) | previous

            # Set the new context.
            ctx.__setitem__(register, value)
            thread.set_context(ctx)

        # Resume the thread.
        finally:
            thread.resume()

    # Very crude way to find data within the process memory.
    # TODO: Perhaps pfind.py can be integrated here instead.
    def find_in_memory(self, query, process):
        for mbi in process.get_memory_map():
            if mbi.State != win32.MEM_COMMIT or mbi.Protect & win32.PAGE_GUARD:
                continue
            address = mbi.BaseAddress
            size = mbi.RegionSize
            try:
                data = process.read(address, size)
            except WindowsError:
                msg = "*** Warning: read error at address %s"
                msg = msg % HexDump.address(address)
                print(msg)
            width = min(len(query), 16)
            p = data.find(query)
            while p >= 0:
                q = p + len(query)
                d = data[p : min(q, p + width)]
                h = HexDump.hexline(d, width=width)
                a = HexDump.address(address + p)
                print("%s: %s" % (a, h))
                p = data.find(query, q)

    # Kill a process.
    def kill_process(self, pid):
        process = self.debug.system.get_process(pid)
        try:
            process.kill()
            if self.debug.is_debugee(pid):
                self.debug.detach(pid)
            print("Killed process (%d)" % pid)
        except Exception:
            print("Error trying to kill process (%d)" % pid)

    # Kill a thread.
    def kill_thread(self, tid):
        thread = self.debug.system.get_thread(tid)
        try:
            thread.kill()
            process = thread.get_process()
            pid = process.get_pid()
            if self.debug.is_debugee(pid) and not process.is_alive():
                self.debug.detach(pid)
            print("Killed thread (%d)" % tid)
        except Exception:
            print("Error trying to kill thread (%d)" % tid)

    # ------------------------------------------------------------------------------
    # Command prompt input

    # Prompt the user for commands.
    def prompt_user(self):
        while not self.debuggerExit:
            try:
                self.cmdloop()
                break
            except CmdError:
                e = sys.exc_info()[1]
```
