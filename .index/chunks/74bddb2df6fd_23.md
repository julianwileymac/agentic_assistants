# Chunk: 74bddb2df6fd_23

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 1653-1716
- chunk: 24/33

```
bug = self.debug
        if arg == "*":
            if self.cmdprefix:
                raise CmdError("prefix not supported")
            breakpoints = debug.get_debugee_pids()
        else:
            targets = self.input_process_list(self.split_tokens(arg))
            if self.cmdprefix:
                targets.insert(0, self.input_process(self.cmdprefix))
            if not targets:
                if self.lastEvent is None:
                    raise CmdError("no current process is set")
                targets = [self.lastEvent.get_pid()]
        for pid in targets:
            bplist = debug.get_process_code_breakpoints(pid)
            printed_process_banner = False
            if bplist:
                if not printed_process_banner:
                    print("Process %d:" % pid)
                    printed_process_banner = True
                for bp in bplist:
                    address = repr(bp)[1:-1].replace("remote address ", "")
                    print("  %s" % address)
            dbplist = debug.get_process_deferred_code_breakpoints(pid)
            if dbplist:
                if not printed_process_banner:
                    print("Process %d:" % pid)
                    printed_process_banner = True
                for label, action, oneshot in dbplist:
                    if oneshot:
                        address = "  Deferred unconditional one-shot" " code breakpoint at %s"
                    else:
                        address = "  Deferred unconditional" " code breakpoint at %s"
                    address = address % label
                    print("  %s" % address)
            bplist = debug.get_process_page_breakpoints(pid)
            if bplist:
                if not printed_process_banner:
                    print("Process %d:" % pid)
                    printed_process_banner = True
                for bp in bplist:
                    address = repr(bp)[1:-1].replace("remote address ", "")
                    print("  %s" % address)
            for tid in debug.system.get_process(pid).iter_thread_ids():
                bplist = debug.get_thread_hardware_breakpoints(tid)
                if bplist:
                    print("Thread %d:" % tid)
                    for bp in bplist:
                        address = repr(bp)[1:-1].replace("remote address ", "")
                        print("  %s" % address)

    def do_bo(self, arg):
        """
        [~process] bo <address> - make a code breakpoint one-shot
        [~thread] bo <address> - make a hardware breakpoint one-shot
        [~process] bo <address-address> - make a memory breakpoint one-shot
        [~process] bo <address> <size> - make a memory breakpoint one-shot
        """
        token_list = self.split_tokens(arg, 1, 2)
        pid, tid, address, size = self.input_breakpoint(token_list)
        debug = self.debug
        found = False
        if size is None:
```
