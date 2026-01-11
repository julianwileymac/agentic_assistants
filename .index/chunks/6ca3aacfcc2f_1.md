# Chunk: 6ca3aacfcc2f_1

- source: `.venv-lab/Lib/site-packages/psutil/_psposix.py`
- lines: 95-163
- chunk: 2/3

```
   flags |= os.WNOHANG
        stop_at = _timer() + timeout

    def sleep(interval):
        # Sleep for some time and return a new increased interval.
        if timeout is not None:
            if _timer() >= stop_at:
                raise TimeoutExpired(timeout, pid=pid, name=proc_name)
        _sleep(interval)
        return _min(interval * 2, 0.04)

    # See: https://linux.die.net/man/2/waitpid
    while True:
        try:
            retpid, status = os.waitpid(pid, flags)
        except InterruptedError:
            interval = sleep(interval)
        except ChildProcessError:
            # This has two meanings:
            # - PID is not a child of os.getpid() in which case
            #   we keep polling until it's gone
            # - PID never existed in the first place
            # In both cases we'll eventually return None as we
            # can't determine its exit status code.
            while _pid_exists(pid):
                interval = sleep(interval)
            return None
        else:
            if retpid == 0:
                # WNOHANG flag was used and PID is still running.
                interval = sleep(interval)
                continue

            if os.WIFEXITED(status):
                # Process terminated normally by calling exit(3) or _exit(2),
                # or by returning from main(). The return value is the
                # positive integer passed to *exit().
                return os.WEXITSTATUS(status)
            elif os.WIFSIGNALED(status):
                # Process exited due to a signal. Return the negative value
                # of that signal.
                return negsig_to_enum(-os.WTERMSIG(status))
            # elif os.WIFSTOPPED(status):
            #     # Process was stopped via SIGSTOP or is being traced, and
            #     # waitpid() was called with WUNTRACED flag. PID is still
            #     # alive. From now on waitpid() will keep returning (0, 0)
            #     # until the process state doesn't change.
            #     # It may make sense to catch/enable this since stopped PIDs
            #     # ignore SIGTERM.
            #     interval = sleep(interval)
            #     continue
            # elif os.WIFCONTINUED(status):
            #     # Process was resumed via SIGCONT and waitpid() was called
            #     # with WCONTINUED flag.
            #     interval = sleep(interval)
            #     continue
            else:
                # Should never happen.
                msg = f"unknown process exit status {status!r}"
                raise ValueError(msg)


def disk_usage(path):
    """Return disk usage associated with path.
    Note: UNIX usually reserves 5% disk space which is not accessible
    by user. In this function "total" and "used" values reflect the
    total and used disk space whereas "free" and "percent" represent
    the "free" and "used percent" user disk space.
```
