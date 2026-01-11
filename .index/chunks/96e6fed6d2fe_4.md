# Chunk: 96e6fed6d2fe_4

- source: `.venv-lab/Lib/site-packages/winpty/ptyprocess.py`
- lines: 318-375
- chunk: 5/5

```
Send control character 4 (Ctrl-D)
        self.pty.write('\x04')

    def sendintr(self):
        """This sends a SIGINT to the child. It does not require
        the SIGINT to be the first character on a line. """
        # Send control character 3 (Ctrl-C)
        self.pty.write('\x03')

    def eof(self):
        """This returns True if the EOF exception was ever raised.
        """
        return self.flag_eof

    def getwinsize(self):
        """Return the window size of the pseudoterminal as a tuple (rows, cols).
        """
        return self._winsize

    def setwinsize(self, rows, cols):
        """Set the terminal window size of the child tty.
        """
        self._winsize = (rows, cols)
        self.pty.set_size(cols, rows)


def _read_in_thread(address, pty: PTY, blocking: bool):
    """Read data from the pty in a thread.
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(address)

    call = 0

    while 1:
        try:
            data = pty.read(blocking=blocking) or b'0011Ignore'
            try:
                client.send(bytes(data, 'utf-8'))
            except socket.error:
                break

            # Handle end of file.
            if pty.iseof():
                try:
                    client.send(b'')
                except socket.error:
                    pass
                finally:
                    break

            call += 1
        except Exception as e:
            break
        time.sleep(1e-3)

    client.close()
```
