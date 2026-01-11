# Chunk: b9a1fc4a85ff_1

- source: `.venv-lab/Lib/site-packages/jupyter_client/channels.py`
- lines: 93-171
- chunk: 2/4

```
 -> None:
        # Class definitions can be torn down during interpreter shutdown.
        # We only need to set _exiting flag if this hasn't happened.
        if HBChannel is not None:
            HBChannel._exiting = True

    def _create_socket(self) -> None:
        if self.socket is not None:
            # close previous socket, before opening a new one
            self.poller.unregister(self.socket)  # type:ignore[unreachable]
            self.socket.close()
        assert self.context is not None
        self.socket = self.context.socket(zmq.REQ)
        self.socket.linger = 1000
        assert self.address is not None
        self.socket.connect(self.address)

        self.poller.register(self.socket, zmq.POLLIN)

    async def _async_run(self) -> None:
        """The thread's main activity.  Call start() instead."""
        self._create_socket()
        self._running = True
        self._beating = True
        assert self.socket is not None

        while self._running:
            if self._pause:
                # just sleep, and skip the rest of the loop
                self._exit.wait(self.time_to_dead)
                continue

            since_last_heartbeat = 0.0
            # no need to catch EFSM here, because the previous event was
            # either a recv or connect, which cannot be followed by EFSM)
            await ensure_async(self.socket.send(b"ping"))
            request_time = time.time()
            # Wait until timeout
            self._exit.wait(self.time_to_dead)
            # poll(0) means return immediately (see http://api.zeromq.org/2-1:zmq-poll)
            self._beating = bool(self.poller.poll(0))
            if self._beating:
                # the poll above guarantees we have something to recv
                await ensure_async(self.socket.recv())
                continue
            elif self._running:
                # nothing was received within the time limit, signal heart failure
                since_last_heartbeat = time.time() - request_time
                self.call_handlers(since_last_heartbeat)
                # and close/reopen the socket, because the REQ/REP cycle has been broken
                self._create_socket()
                continue

    def run(self) -> None:
        """Run the heartbeat thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._async_run())
        finally:
            loop.close()

    def pause(self) -> None:
        """Pause the heartbeat."""
        self._pause = True

    def unpause(self) -> None:
        """Unpause the heartbeat."""
        self._pause = False

    def is_beating(self) -> bool:
        """Is the heartbeat running and responsive (and not paused)."""
        if self.is_alive() and not self._pause and self._beating:  # noqa
            return True
        else:
            return False

    def stop(self) -> None:
```
