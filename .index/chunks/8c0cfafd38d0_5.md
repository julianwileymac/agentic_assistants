# Chunk: 8c0cfafd38d0_5

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/_pydevd_bundle/pydevd_stackless.py`
- lines: 316-386
- chunk: 6/7

```
========
    # setup
    # =======================================================================================================================
    def setup(self, *args, **kwargs):
        """
        Called to run a new tasklet: rebind the creation so that we can trace it.
        """

        f = self.tempval

        def new_f(old_f, args, kwargs):
            debugger = get_global_debugger()
            if debugger is not None:
                debugger.enable_tracing()

            debugger = None

            # Remove our own traces :)
            self.tempval = old_f
            register_tasklet_info(self)

            # Hover old_f to see the stackless being created and *args and **kwargs to see its parameters.
            return old_f(*args, **kwargs)

        # This is the way to tell stackless that the function it should execute is our function, not the original one. Note:
        # setting tempval is the same as calling bind(new_f), but it seems that there's no other way to get the currently
        # bound function, so, keeping on using tempval instead of calling bind (which is actually the same thing in a better
        # API).

        self.tempval = new_f

        return _original_setup(self, f, args, kwargs)

    # =======================================================================================================================
    # __call__
    # =======================================================================================================================
    def __call__(self, *args, **kwargs):
        """
        Called to run a new tasklet: rebind the creation so that we can trace it.
        """

        return setup(self, *args, **kwargs)

    _original_run = stackless.run

    # =======================================================================================================================
    # run
    # =======================================================================================================================
    def run(*args, **kwargs):
        debugger = get_global_debugger()
        if debugger is not None:
            debugger.enable_tracing()
        debugger = None

        return _original_run(*args, **kwargs)


# =======================================================================================================================
# patch_stackless
# =======================================================================================================================
def patch_stackless():
    """
    This function should be called to patch the stackless module so that new tasklets are properly tracked in the
    debugger.
    """
    global _application_set_schedule_callback
    _application_set_schedule_callback = stackless.set_schedule_callback(_schedule_callback)

    def set_schedule_callback(callable):
        global _application_set_schedule_callback
```
