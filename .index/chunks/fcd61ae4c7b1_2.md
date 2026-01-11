# Chunk: fcd61ae4c7b1_2

- source: `.venv-lab/Lib/site-packages/jupyter_client/consoleapp.py`
- lines: 158-229
- chunk: 3/6

```
:ignore[attr-defined]

    def init_connection_file(self) -> None:
        """find the connection file, and load the info if found.

        The current working directory and the current profile's security
        directory will be searched for the file if it is not given by
        absolute path.

        When attempting to connect to an existing kernel and the `--existing`
        argument does not match an existing file, it will be interpreted as a
        fileglob, and the matching file in the current profile's security dir
        with the latest access time will be used.

        After this method is called, self.connection_file contains the *full path*
        to the connection file, never just its name.
        """
        runtime_dir = self.runtime_dir  # type:ignore[attr-defined]
        if self.existing:
            try:
                cf = find_connection_file(self.existing, [".", runtime_dir])
            except Exception:
                self.log.critical(
                    "Could not find existing kernel connection file %s", self.existing
                )
                self.exit(1)  # type:ignore[attr-defined]
            self.log.debug("Connecting to existing kernel: %s", cf)
            self.connection_file = cf
        else:
            # not existing, check if we are going to write the file
            # and ensure that self.connection_file is a full path, not just the shortname
            try:
                cf = find_connection_file(self.connection_file, [runtime_dir])
            except Exception:
                # file might not exist
                if self.connection_file == os.path.basename(self.connection_file):
                    # just shortname, put it in security dir
                    cf = os.path.join(runtime_dir, self.connection_file)
                else:
                    cf = self.connection_file
                self.connection_file = cf
        try:
            self.connection_file = _filefind(self.connection_file, [".", runtime_dir])
        except OSError:
            self.log.debug("Connection File not found: %s", self.connection_file)
            return

        # should load_connection_file only be used for existing?
        # as it is now, this allows reusing ports if an existing
        # file is requested
        try:
            self.load_connection_file()
        except Exception:
            self.log.error(
                "Failed to load connection file: %r",
                self.connection_file,
                exc_info=True,
            )
            self.exit(1)  # type:ignore[attr-defined]

    def init_ssh(self) -> None:
        """set up ssh tunnels, if needed."""
        if not self.existing or (not self.sshserver and not self.sshkey):
            return
        self.load_connection_file()

        transport = self.transport
        ip = self.ip

        if transport != "tcp":
            self.log.error("Can only use ssh tunnels with TCP sockets, not %s", transport)
```
