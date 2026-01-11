# Chunk: cc4c3c8aea41_7

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/kernels/kernelmanager.py`
- lines: 487-570
- chunk: 8/14

```
     channel.on_recv(on_reply)  # type:ignore[operator]
        loop = IOLoop.current()
        timeout = loop.add_timeout(loop.time() + self.kernel_info_timeout, on_timeout)
        # Re-establish activity watching if ports have changed...
        if self._get_changed_ports(kernel_id) is not None:
            self.stop_watching_activity(kernel_id)
            self.start_watching_activity(kernel_id)
        return future

    restart_kernel = _async_restart_kernel

    def notify_connect(self, kernel_id):
        """Notice a new connection to a kernel"""
        if kernel_id in self._kernel_connections:
            self._kernel_connections[kernel_id] += 1

    def notify_disconnect(self, kernel_id):
        """Notice a disconnection from a kernel"""
        if kernel_id in self._kernel_connections:
            self._kernel_connections[kernel_id] -= 1

    def kernel_model(self, kernel_id):
        """Return a JSON-safe dict representing a kernel

        For use in representing kernels in the JSON APIs.
        """
        self._check_kernel_id(kernel_id)
        kernel = self._kernels[kernel_id]

        model = {
            "id": kernel_id,
            "name": kernel.kernel_name,
            "last_activity": isoformat(kernel.last_activity),
            "execution_state": kernel.execution_state,
            "connections": self._kernel_connections.get(kernel_id, 0),
        }
        if getattr(kernel, "reason", None):
            model["reason"] = kernel.reason
        return model

    def list_kernels(self):
        """Returns a list of kernel_id's of kernels running."""
        kernels = []
        kernel_ids = self.pinned_superclass.list_kernel_ids(self)
        for kernel_id in kernel_ids:
            try:
                model = self.kernel_model(kernel_id)
                kernels.append(model)
            except (web.HTTPError, KeyError):
                # Probably due to a (now) non-existent kernel, continue building the list
                pass
        return kernels

    # override _check_kernel_id to raise 404 instead of KeyError
    def _check_kernel_id(self, kernel_id):
        """Check a that a kernel_id exists and raise 404 if not."""
        if kernel_id not in self:
            raise web.HTTPError(404, "Kernel does not exist: %s" % kernel_id)

    # monitoring activity:
    untracked_message_types = List(
        trait=Unicode(),
        config=True,
        default_value=[
            "comm_info_request",
            "comm_info_reply",
            "kernel_info_request",
            "kernel_info_reply",
            "shutdown_request",
            "shutdown_reply",
            "interrupt_request",
            "interrupt_reply",
            "debug_request",
            "debug_reply",
            "stream",
            "display_data",
            "update_display_data",
            "execute_input",
            "execute_result",
            "error",
            "status",
            "clear_output",
            "debug_event",
```
