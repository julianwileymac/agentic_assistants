# Chunk: cc4c3c8aea41_3

- source: `.venv-lab/Lib/site-packages/jupyter_server/services/kernels/kernelmanager.py`
- lines: 232-301
- chunk: 4/14

```
 not in self:
            if path is not None:
                kwargs["cwd"] = self.cwd_for_path(path, env=kwargs.get("env", {}))
            if kernel_id is not None:
                assert kernel_id is not None, "Never Fail, but necessary for mypy "
                kwargs["kernel_id"] = kernel_id
            kernel_id = await self.pinned_superclass._async_start_kernel(self, **kwargs)
            self._kernel_connections[kernel_id] = 0

            # add busy/activity markers:
            kernel = self.get_kernel(kernel_id)
            kernel.execution_state = "starting"  # type:ignore[attr-defined]
            kernel.reason = ""  # type:ignore[attr-defined]
            kernel.last_activity = utcnow()  # type:ignore[attr-defined]
            self.log.info("Kernel started: %s", kernel_id)
            self.log.debug(
                "Kernel args (excluding env): %r", {k: v for k, v in kwargs.items() if k != "env"}
            )
            env = kwargs.get("env", None)
            if env and isinstance(env, dict):  # type:ignore[unreachable]
                self.log.debug("Kernel argument 'env' passed with: %r", list(env.keys()))  # type:ignore[unreachable]

            task = asyncio.create_task(self._finish_kernel_start(kernel_id))
            if not getattr(self, "use_pending_kernels", None):
                await task
            else:
                self._pending_kernel_tasks[kernel_id] = task

            # Increase the metric of number of kernels running
            # for the relevant kernel type by 1
            KERNEL_CURRENTLY_RUNNING_TOTAL.labels(type=self._kernels[kernel_id].kernel_name).inc()

        else:
            self.log.info("Using existing kernel: %s", kernel_id)

        # Initialize culling if not already
        if not self._initialized_culler:
            self.initialize_culler()
        assert kernel_id is not None
        return kernel_id

    # see https://github.com/jupyter-server/jupyter_server/issues/1165
    # this assignment is technically incorrect, but might need a change of API
    # in jupyter_client.
    start_kernel = _async_start_kernel  # type:ignore[assignment]

    async def _finish_kernel_start(self, kernel_id):
        """Handle a kernel that finishes starting."""
        km = self.get_kernel(kernel_id)
        if hasattr(km, "ready"):
            ready = km.ready
            if not isinstance(ready, asyncio.Future):
                ready = asyncio.wrap_future(ready)
            try:
                await ready
            except Exception:
                self.log.exception("Error waiting for kernel manager ready")
                return

        self._kernel_ports[kernel_id] = km.ports
        self.start_watching_activity(kernel_id)
        # register callback for failed auto-restart
        self.add_restart_callback(
            kernel_id,
            lambda: self._handle_kernel_died(kernel_id),
            "dead",
        )

    def ports_changed(self, kernel_id):
```
