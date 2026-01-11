# Chunk: bbbf0c1a22c6_5

- source: `.venv-lab/Lib/site-packages/zmq/eventloop/zmqstream.py`
- lines: 417-493
- chunk: 6/9

```
mit: int | None = None):
        """Flush pending messages.

        This method safely handles all pending incoming and/or outgoing messages,
        bypassing the inner loop, passing them to the registered callbacks.

        A limit can be specified, to prevent blocking under high load.

        flush will return the first time ANY of these conditions are met:
            * No more events matching the flag are pending.
            * the total number of events handled reaches the limit.

        Note that if ``flag|POLLIN != 0``, recv events will be flushed even if no callback
        is registered, unlike normal IOLoop operation. This allows flush to be
        used to remove *and ignore* incoming messages.

        Parameters
        ----------
        flag : int
            default=POLLIN|POLLOUT
            0MQ poll flags.
            If flag|POLLIN,  recv events will be flushed.
            If flag|POLLOUT, send events will be flushed.
            Both flags can be set at once, which is the default.
        limit : None or int, optional
            The maximum number of messages to send or receive.
            Both send and recv count against this limit.

        Returns
        -------
        int :
            count of events handled (both send and recv)
        """
        self._check_closed()
        # unset self._flushed, so callbacks will execute, in case flush has
        # already been called this iteration
        already_flushed = self._flushed
        self._flushed = False
        # initialize counters
        count = 0

        def update_flag():
            """Update the poll flag, to prevent registering POLLOUT events
            if we don't have pending sends."""
            return flag & zmq.POLLIN | (self.sending() and flag & zmq.POLLOUT)

        flag = update_flag()
        if not flag:
            # nothing to do
            return 0
        self.poller.register(self.socket, flag)
        events = self.poller.poll(0)
        while events and (not limit or count < limit):
            s, event = events[0]
            if event & POLLIN:  # receiving
                self._handle_recv()
                count += 1
                if self.socket is None:
                    # break if socket was closed during callback
                    break
            if event & POLLOUT and self.sending():
                self._handle_send()
                count += 1
                if self.socket is None:
                    # break if socket was closed during callback
                    break

            flag = update_flag()
            if flag:
                self.poller.register(self.socket, flag)
                events = self.poller.poll(0)
            else:
                events = []
        if count:  # only bypass loop if we actually flushed something
            # skip send/recv callbacks this iteration
            self._flushed = True
```
