# Chunk: 96e6fed6d2fe_0

- source: `.venv-lab/Lib/site-packages/winpty/ptyprocess.py`
- lines: 1-94
- chunk: 1/5

```
# -*- coding: utf-8 -*-

# Standard library imports
import codecs
import os
import shlex
import signal
import socket
import subprocess
import threading
import time
from shutil import which

# Local imports
from .winpty import PTY


class PtyProcess(object):
    """This class represents a process running in a pseudoterminal.

    The main constructor is the :meth:`spawn` classmethod.
    """

    def __init__(self, pty):
        assert isinstance(pty, PTY)
        self.pty = pty
        self.pid = pty.pid
        # self.fd = pty.fd
        self.argv = None
        self.env = None
        self.launch_dir = None

        self.read_blocking = bool(int(os.environ.get('PYWINPTY_BLOCK', 1)))
        self.closed = False
        self.flag_eof = False

        # Used by terminate() to give kernel time to update process status.
        # Time in seconds.
        self.delayafterterminate = 0.1
        # Used by close() to give kernel time to update process status.
        # Time in seconds.
        self.delayafterclose = 0.1

        # Set up our file reader sockets.
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.bind(("127.0.0.1", 0))
        address = self._server.getsockname()
        self._server.listen(1)

        # Read from the pty in a thread.
        self._thread = threading.Thread(target=_read_in_thread,
            args=(address, self.pty, self.read_blocking))
        self._thread.daemon = True
        self._thread.start()

        self.fileobj, _ = self._server.accept()
        self.fd = self.fileobj.fileno()

    @classmethod
    def spawn(cls, argv, cwd=None, env=None, dimensions=(24, 80),
              backend=None):
        """Start the given command in a child process in a pseudo terminal.

        This does all the setting up the pty, and returns an instance of
        PtyProcess.

        Dimensions of the psuedoterminal used for the subprocess can be
        specified as a tuple (rows, cols), or the default (24, 80) will be
        used.
        """
        if isinstance(argv, str):
            argv = shlex.split(argv, posix=False)

        if not isinstance(argv, (list, tuple)):
            raise TypeError("Expected a list or tuple for argv, got %r" % argv)

        # Shallow copy of argv so we can modify it
        _argv: list[str] = list(argv[:])
        command = _argv[0]
        env = env or os.environ

        path = env.get('PATH', os.defpath)
        command_with_path = which(command, path=path)
        if command_with_path is None:
            raise FileNotFoundError(
                'The command was not found or was not ' +
                'executable: %s.' % command
            )
        command = command_with_path
        _argv[0] = command
        cmdline = ' ' + subprocess.list2cmdline(_argv[1:])
        cwd = cwd or os.getcwd()

```
