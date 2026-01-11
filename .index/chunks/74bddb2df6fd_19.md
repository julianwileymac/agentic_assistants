# Chunk: 74bddb2df6fd_19

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/interactive.py`
- lines: 1381-1450
- chunk: 20/33

```
 %s" % (tid, name))
        else:
            system = self.debug.system
            pid_list = self.debug.get_debugee_pids()
            if pid_list:
                print("Thread ID    Thread name")
                for pid in pid_list:
                    process = system.get_process(pid)
                    for thread in process.iter_threads():
                        tid = thread.get_tid()
                        name = thread.get_name()
                        print("%-12d %s" % (tid, name))

    do_tl = do_threadlist

    def do_kill(self, arg):
        """
        [~process] kill - kill a process
        [~thread] kill - kill a thread
        kill - kill the current process
        kill * - kill all debugged processes
        kill <processes and/or threads...> - kill the given processes and threads
        """
        if arg:
            if arg == "*":
                target_pids = self.debug.get_debugee_pids()
                target_tids = list()
            else:
                target_pids = set()
                target_tids = set()
                if self.cmdprefix:
                    pid, tid = self.get_process_and_thread_ids_from_prefix()
                    if tid is None:
                        target_tids.add(tid)
                    else:
                        target_pids.add(pid)
                for token in self.split_tokens(arg):
                    try:
                        pid = self.input_process(token)
                        target_pids.add(pid)
                    except CmdError:
                        try:
                            tid = self.input_process(token)
                            target_pids.add(pid)
                        except CmdError:
                            msg = "unknown process or thread (%s)" % token
                            raise CmdError(msg)
                target_pids = list(target_pids)
                target_tids = list(target_tids)
                target_pids.sort()
                target_tids.sort()
            msg = "You are about to kill %d processes and %d threads."
            msg = msg % (len(target_pids), len(target_tids))
            if self.ask_user(msg):
                for pid in target_pids:
                    self.kill_process(pid)
                for tid in target_tids:
                    self.kill_thread(tid)
        else:
            if self.cmdprefix:
                pid, tid = self.get_process_and_thread_ids_from_prefix()
                if tid is None:
                    if self.lastEvent is not None and pid == self.lastEvent.get_pid():
                        msg = "You are about to kill the current process."
                    else:
                        msg = "You are about to kill process %d." % pid
                    if self.ask_user(msg):
                        self.kill_process(pid)
                else:
```
