# Chunk: 74bddb2df6fd_18

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 1301-1389
- chunk: 19/33

```
f.debug.get_debugee_count() > 0:
            return True

    do_g = do_continue
    do_go = do_continue

    def do_gh(self, arg):
        """
        gh - go with exception handled
        """
        if self.cmdprefix:
            raise CmdError("prefix not allowed")
        if arg:
            raise CmdError("too many arguments")
        if self.lastEvent:
            self.lastEvent.continueStatus = win32.DBG_EXCEPTION_HANDLED
        return self.do_go(arg)

    def do_gn(self, arg):
        """
        gn - go with exception not handled
        """
        if self.cmdprefix:
            raise CmdError("prefix not allowed")
        if arg:
            raise CmdError("too many arguments")
        if self.lastEvent:
            self.lastEvent.continueStatus = win32.DBG_EXCEPTION_NOT_HANDLED
        return self.do_go(arg)

    def do_refresh(self, arg):
        """
        refresh - refresh the list of running processes and threads
        [~process] refresh - refresh the list of running threads
        """
        if arg:
            raise CmdError("too many arguments")
        if self.cmdprefix:
            process = self.get_process_from_prefix()
            process.scan()
        else:
            self.debug.system.scan()

    def do_processlist(self, arg):
        """
        pl - show the processes being debugged
        processlist - show the processes being debugged
        """
        if self.cmdprefix:
            raise CmdError("prefix not allowed")
        if arg:
            raise CmdError("too many arguments")
        system = self.debug.system
        pid_list = self.debug.get_debugee_pids()
        if pid_list:
            print("Process ID   File name")
            for pid in pid_list:
                if pid == 0:
                    filename = "System Idle Process"
                elif pid == 4:
                    filename = "System"
                else:
                    filename = system.get_process(pid).get_filename()
                    filename = PathOperations.pathname_to_filename(filename)
                print("%-12d %s" % (pid, filename))

    do_pl = do_processlist

    def do_threadlist(self, arg):
        """
        tl - show the threads being debugged
        threadlist - show the threads being debugged
        """
        if arg:
            raise CmdError("too many arguments")
        if self.cmdprefix:
            process = self.get_process_from_prefix()
            for thread in process.iter_threads():
                tid = thread.get_tid()
                name = thread.get_name()
                print("%-12d %s" % (tid, name))
        else:
            system = self.debug.system
            pid_list = self.debug.get_debugee_pids()
            if pid_list:
                print("Thread ID    Thread name")
                for pid in pid_list:
                    process = system.get_process(pid)
```
