# Chunk: b26e1acacaf8_1

- source: `.venv-lab/Lib/site-packages/ipykernel/comm/comm.py`
- lines: 88-101
- chunk: 2/2

```
guments between base classes.
        had_kernel = "kernel" in kwargs
        kernel = kwargs.pop("kernel", None)
        if target_name:
            kwargs["target_name"] = target_name
        BaseComm.__init__(self, data=data, metadata=metadata, buffers=buffers, **kwargs)  # type:ignore[call-arg]
        # only re-add kernel if explicitly provided
        if had_kernel:
            kwargs["kernel"] = kernel
        traitlets.config.LoggingConfigurable.__init__(self, **kwargs)


__all__ = ["Comm"]
```
