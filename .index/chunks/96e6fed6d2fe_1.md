# Chunk: 96e6fed6d2fe_1

- source: `.venv-lab/Lib/site-packages/winpty/ptyprocess.py`
- lines: 85-166
- chunk: 2/5

```
FileNotFoundError(
                'The command was not found or was not ' +
                'executable: %s.' % command
            )
        command = command_with_path
        _argv[0] = command
        cmdline = ' ' + subprocess.list2cmdline(_argv[1:])
        cwd = cwd or os.getcwd()

        backend = backend or os.environ.get('PYWINPTY_BACKEND', None)
        backend = int(backend) if backend is not None else backend

        proc = PTY(dimensions[1], dimensions[0],
                   backend=backend)

        # Create the environment string.
        envStrs = []
        for (key, value) in env.items():
            envStrs.append('%s=%s' % (key, value))
        env = '\0'.join(envStrs) + '\0'

        # command = bytes(command, encoding)
        # cwd = bytes(cwd, encoding)
        # cmdline = bytes(cmdline, encoding)
        # env = bytes(env, encoding)

        if len(_argv) == 1:
            proc.spawn(command, cwd=cwd, env=env)
        else:
            proc.spawn(command, cwd=cwd, env=env, cmdline=cmdline)

        inst = cls(proc)
        inst._winsize = dimensions

        # Set some informational attributes
        inst.argv = _argv
        if env is not None:
            inst.env = env
        if cwd is not None:
            inst.launch_dir = cwd

        return inst

    @property
    def exitstatus(self):
        """The exit status of the process.
        """
        return self.pty.get_exitstatus()

    def fileno(self):
        """This returns the file descriptor of the pty for the child.
        """
        return self.fd

    def close(self, force=False):
        """This closes the connection with the child application. Note that
        calling close() more than once is valid. This emulates standard Python
        behavior with files. Set force to True if you want to make sure that
        the child is terminated (SIGKILL is sent if the child ignores
        SIGINT)."""
        if not self.closed:
            self.fileobj.close()
            self._server.close()
            # Give kernel time to update process status.
            time.sleep(self.delayafterclose)
            if self.isalive():
                if not self.terminate(force):
                    raise IOError('Could not terminate the child.')
            self.fd = -1
            self.closed = True
            # del self.pty

    def __del__(self):
        """This makes sure that no system resources are left open. Python only
        garbage collects Python objects. OS file descriptors are not Python
        objects, so they must be handled explicitly. If the child file
        descriptor was opened outside of this class (passed to the constructor)
        then this does not close it.
        """
        # It is possible for __del__ methods to execute during the
        # teardown of the Python VM itself. Thus self.close() may
```
