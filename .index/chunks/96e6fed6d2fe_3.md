# Chunk: 96e6fed6d2fe_3

- source: `.venv-lab/Lib/site-packages/winpty/ptyprocess.py`
- lines: 245-327
- chunk: 4/5

```
ion:
            pass
        time.sleep(self.delayafterterminate)
        if not self.isalive():
            return True
        if force:
            self.kill(signal.SIGTERM)
            time.sleep(self.delayafterterminate)
            if not self.isalive():
                return True
            else:
                return False

    def wait(self):
        """This waits until the child exits. This is a blocking call. This will
        not read any data from the child.
        """
        while self.isalive():
            time.sleep(0.1)
        return self.exitstatus

    def isalive(self):
        """This tests if the child process is running or not. This is
        non-blocking. If the child was terminated then this will read the
        exitstatus or signalstatus of the child. This returns True if the child
        process appears to be running or False if not.
        """
        alive = self.pty.isalive()
        self.closed = not alive
        return alive

    def kill(self, sig):
        """Kill the process with the given signal.
        """
        if self.pid is None:
            return
        os.kill(self.pid, sig)

    def sendcontrol(self, char):
        '''Helper method that wraps send() with mnemonic access for sending control
        character to the child (such as Ctrl-C or Ctrl-D).  For example, to send
        Ctrl-G (ASCII 7, bell, '\a')::
            child.sendcontrol('g')
        See also, sendintr() and sendeof().
        '''
        char = char.lower()
        a = ord(char)
        if 97 <= a <= 122:
            a = a - ord('a') + 1
            byte = bytes([a]).decode("ascii")
            return self.pty.write(byte), byte
        d = {'@': 0, '`': 0,
            '[': 27, '{': 27,
            '\\': 28, '|': 28,
            ']': 29, '}': 29,
            '^': 30, '~': 30,
            '_': 31,
            '?': 127}
        if char not in d:
            return 0, ''

        byte = bytes([d[char]]).decode("ascii")
        return self.pty.write(byte), byte

    def sendeof(self):
        """This sends an EOF to the child. This sends a character which causes
        the pending parent output buffer to be sent to the waiting child
        program without waiting for end-of-line. If it is the first character
        of the line, the read() in the user program returns 0, which signifies
        end-of-file. This means to work as expected a sendeof() has to be
        called at the beginning of a line. This method does not send a newline.
        It is the responsibility of the caller to ensure the eof is sent at the
        beginning of a line."""
        # Send control character 4 (Ctrl-D)
        self.pty.write('\x04')

    def sendintr(self):
        """This sends a SIGINT to the child. It does not require
        the SIGINT to be the first character on a line. """
        # Send control character 3 (Ctrl-C)
        self.pty.write('\x03')

```
