# Chunk: cc4c3c8aea41_6

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/kernels/kernelmanager.py`
- lines: 422-492
- chunk: 7/14

```
         self.log.info(
                "Discarding %s buffered messages for %s",
                len(msg_buffer),
                buffer_info["session_key"],
            )

    async def _async_shutdown_kernel(self, kernel_id, now=False, restart=False):
        """Shutdown a kernel by kernel_id"""
        self._check_kernel_id(kernel_id)

        # Decrease the metric of number of kernels
        # running for the relevant kernel type by 1
        KERNEL_CURRENTLY_RUNNING_TOTAL.labels(type=self._kernels[kernel_id].kernel_name).dec()

        if kernel_id in self._pending_kernel_tasks:
            task = self._pending_kernel_tasks.pop(kernel_id)
            task.cancel()

        self.stop_watching_activity(kernel_id)
        self.stop_buffering(kernel_id)

        return await self.pinned_superclass._async_shutdown_kernel(
            self, kernel_id, now=now, restart=restart
        )

    shutdown_kernel = _async_shutdown_kernel

    async def _async_restart_kernel(self, kernel_id, now=False):
        """Restart a kernel by kernel_id"""
        self._check_kernel_id(kernel_id)
        await self.pinned_superclass._async_restart_kernel(self, kernel_id, now=now)
        kernel = self.get_kernel(kernel_id)
        # return a Future that will resolve when the kernel has successfully restarted
        channel = kernel.connect_shell()
        future: Future[Any] = Future()

        def finish():
            """Common cleanup when restart finishes/fails for any reason."""
            if not channel.closed():  # type:ignore[operator]
                channel.close()
            loop.remove_timeout(timeout)
            kernel.remove_restart_callback(on_restart_failed, "dead")
            kernel._pending_restart_cleanup = None  # type:ignore[attr-defined]

        def on_reply(msg):
            self.log.debug("Kernel info reply received: %s", kernel_id)
            finish()
            if not future.done():
                future.set_result(msg)

        def on_timeout():
            self.log.warning("Timeout waiting for kernel_info_reply: %s", kernel_id)
            finish()
            if not future.done():
                future.set_exception(TimeoutError("Timeout waiting for restart"))

        def on_restart_failed():
            self.log.warning("Restarting kernel failed: %s", kernel_id)
            finish()
            if not future.done():
                future.set_exception(RuntimeError("Restart failed"))

        kernel.add_restart_callback(on_restart_failed, "dead")
        kernel._pending_restart_cleanup = finish  # type:ignore[attr-defined]
        kernel.session.send(channel, "kernel_info_request")
        channel.on_recv(on_reply)  # type:ignore[operator]
        loop = IOLoop.current()
        timeout = loop.add_timeout(loop.time() + self.kernel_info_timeout, on_timeout)
        # Re-establish activity watching if ports have changed...
        if self._get_changed_ports(kernel_id) is not None:
```
