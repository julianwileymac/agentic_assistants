# Chunk: cc4c3c8aea41_9

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/kernels/kernelmanager.py`
- lines: 624-698
- chunk: 10/14

```
activity on %s: %s (%s)",
                    kernel_id,
                    msg_type,
                    kernel.execution_state,
                )
            else:
                self.log.debug("activity on %s: %s", kernel_id, msg_type)

        kernel._activity_stream.on_recv(record_activity)

    def stop_watching_activity(self, kernel_id):
        """Stop watching IOPub messages on a kernel for activity."""
        kernel = self._kernels[kernel_id]
        if getattr(kernel, "_activity_stream", None):
            if not kernel._activity_stream.socket.closed:
                kernel._activity_stream.close()
            kernel._activity_stream = None
        if getattr(kernel, "_pending_restart_cleanup", None):
            kernel._pending_restart_cleanup()

    def initialize_culler(self):
        """Start idle culler if 'cull_idle_timeout' is greater than zero.

        Regardless of that value, set flag that we've been here.
        """
        if (
            not self._initialized_culler
            and self.cull_idle_timeout > 0
            and self._culler_callback is None
        ):
            _ = IOLoop.current()
            if self.cull_interval <= 0:  # handle case where user set invalid value
                self.log.warning(
                    "Invalid value for 'cull_interval' detected (%s) - using default value (%s).",
                    self.cull_interval,
                    self.cull_interval_default,
                )
                self.cull_interval = self.cull_interval_default
            self._culler_callback = PeriodicCallback(self.cull_kernels, 1000 * self.cull_interval)
            self.log.info(
                "Culling kernels with idle durations > %s seconds at %s second intervals ...",
                self.cull_idle_timeout,
                self.cull_interval,
            )
            if self.cull_busy:
                self.log.info("Culling kernels even if busy")
            if self.cull_connected:
                self.log.info("Culling kernels even with connected clients")
            self._culler_callback.start()

        self._initialized_culler = True

    async def cull_kernels(self):
        """Handle culling kernels."""
        self.log.debug(
            "Polling every %s seconds for kernels idle > %s seconds...",
            self.cull_interval,
            self.cull_idle_timeout,
        )
        """Create a separate list of kernels to avoid conflicting updates while iterating"""
        for kernel_id in list(self._kernels):
            try:
                await self.cull_kernel_if_idle(kernel_id)
            except Exception as e:
                self.log.exception(
                    "The following exception was encountered while checking the idle duration of kernel %s: %s",
                    kernel_id,
                    e,
                )

    async def cull_kernel_if_idle(self, kernel_id):
        """Cull a kernel if it is idle."""
        kernel = self._kernels[kernel_id]
```
