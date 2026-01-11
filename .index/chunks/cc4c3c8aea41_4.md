# Chunk: cc4c3c8aea41_4

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/kernels/kernelmanager.py`
- lines: 291-358
- chunk: 5/14

```
d] = km.ports
        self.start_watching_activity(kernel_id)
        # register callback for failed auto-restart
        self.add_restart_callback(
            kernel_id,
            lambda: self._handle_kernel_died(kernel_id),
            "dead",
        )

    def ports_changed(self, kernel_id):
        """Used by ZMQChannelsHandler to determine how to coordinate nudge and replays.

        Ports are captured when starting a kernel (via MappingKernelManager).  Ports
        are considered changed (following restarts) if the referenced KernelManager
        is using a set of ports different from those captured at startup.  If changes
        are detected, the captured set is updated and a value of True is returned.

        NOTE: Use is exclusive to ZMQChannelsHandler because this object is a singleton
        instance while ZMQChannelsHandler instances are per WebSocket connection that
        can vary per kernel lifetime.
        """
        changed_ports = self._get_changed_ports(kernel_id)
        if changed_ports:
            # If changed, update captured ports and return True, else return False.
            self.log.debug("Port change detected for kernel: %s", kernel_id)
            self._kernel_ports[kernel_id] = changed_ports
            return True
        return False

    def _get_changed_ports(self, kernel_id):
        """Internal method to test if a kernel's ports have changed and, if so, return their values.

        This method does NOT update the captured ports for the kernel as that can only be done
        by ZMQChannelsHandler, but instead returns the new list of ports if they are different
        than those captured at startup.  This enables the ability to conditionally restart
        activity monitoring immediately following a kernel's restart (if ports have changed).
        """
        # Get current ports and return comparison with ports captured at startup.
        km = self.get_kernel(kernel_id)
        assert isinstance(km.ports, list)
        assert isinstance(self._kernel_ports[kernel_id], list)
        if km.ports != self._kernel_ports[kernel_id]:
            return km.ports
        return None

    def start_buffering(self, kernel_id, session_key, channels):
        """Start buffering messages for a kernel

        Parameters
        ----------
        kernel_id : str
            The id of the kernel to stop buffering.
        session_key : str
            The session_key, if any, that should get the buffer.
            If the session_key matches the current buffered session_key,
            the buffer will be returned.
        channels : dict({'channel': ZMQStream})
            The zmq channels whose messages should be buffered.
        """

        if not self.buffer_offline_messages:
            for stream in channels.values():
                stream.close()
            return

        self.log.info("Starting buffering for %s", session_key)
        self._check_kernel_id(kernel_id)
```
