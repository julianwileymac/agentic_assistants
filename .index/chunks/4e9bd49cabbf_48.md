# Chunk: 4e9bd49cabbf_48

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 3627-3711
- chunk: 49/64

```
} otherwise.
        """
        self.__cleanup_module(event)
        return True

    def _notify_exit_thread(self, event):
        """
        Notify the termination of a thread.

        @type  event: L{ExitThreadEvent}
        @param event: Exit thread event.

        @rtype:  bool
        @return: C{True} to call the user-defined handler, C{False} otherwise.
        """
        self.__cleanup_thread(event)
        return True

    def _notify_exit_process(self, event):
        """
        Notify the termination of a process.

        @type  event: L{ExitProcessEvent}
        @param event: Exit process event.

        @rtype:  bool
        @return: C{True} to call the user-defined handler, C{False} otherwise.
        """
        self.__cleanup_process(event)
        self.__cleanup_thread(event)
        return True

    # ------------------------------------------------------------------------------

    # This is the high level breakpoint interface. Here we don't have to care
    # about defining or enabling breakpoints, and many errors are ignored
    # (like for example setting the same breakpoint twice, here the second
    # breakpoint replaces the first, much like in WinDBG). It should be easier
    # and more intuitive, if less detailed. It also allows the use of deferred
    # breakpoints.

    # ------------------------------------------------------------------------------

    # Code breakpoints

    def __set_break(self, pid, address, action, oneshot):
        """
        Used by L{break_at} and L{stalk_at}.

        @type  pid: int
        @param pid: Process global ID.

        @type  address: int or str
        @param address:
            Memory address of code instruction to break at. It can be an
            integer value for the actual address or a string with a label
            to be resolved.

        @type  action: function
        @param action: (Optional) Action callback function.

            See L{define_code_breakpoint} for more details.

        @type  oneshot: bool
        @param oneshot: C{True} for one-shot breakpoints, C{False} otherwise.

        @rtype:  L{Breakpoint}
        @return: Returns the new L{Breakpoint} object, or C{None} if the label
            couldn't be resolved and the breakpoint was deferred. Deferred
            breakpoints are set when the DLL they point to is loaded.
        """
        if type(address) not in (int, long):
            label = address
            try:
                address = self.system.get_process(pid).resolve_label(address)
                if not address:
                    raise Exception()
            except Exception:
                try:
                    deferred = self.__deferredBP[pid]
                except KeyError:
                    deferred = dict()
                    self.__deferredBP[pid] = deferred
                if label in deferred:
```
