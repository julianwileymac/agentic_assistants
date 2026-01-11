# Chunk: 4e9bd49cabbf_5

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 419-504
- chunk: 6/64

```
.
        """
        statemsg = ""
        oldState = self.stateNames[self.get_state()]
        newState = self.stateNames[state]
        msg = "Invalid state transition (%s -> %s)" " for breakpoint at address %s"
        msg = msg % (oldState, newState, HexDump.address(self.get_address()))
        raise AssertionError(msg)

    def disable(self, aProcess, aThread):
        """
        Transition to L{DISABLED} state.
          - When hit: OneShot S{->} Disabled
          - Forced by user: Enabled, OneShot, Running S{->} Disabled
          - Transition from running state may require special handling
            by the breakpoint implementation class.

        @type  aProcess: L{Process}
        @param aProcess: Process object.

        @type  aThread: L{Thread}
        @param aThread: Thread object.
        """
        ##        if self.__state not in (self.ENABLED, self.ONESHOT, self.RUNNING):
        ##            self.__bad_transition(self.DISABLED)
        self.__state = self.DISABLED

    def enable(self, aProcess, aThread):
        """
        Transition to L{ENABLED} state.
          - When hit: Running S{->} Enabled
          - Forced by user: Disabled, Running S{->} Enabled
          - Transition from running state may require special handling
            by the breakpoint implementation class.

        @type  aProcess: L{Process}
        @param aProcess: Process object.

        @type  aThread: L{Thread}
        @param aThread: Thread object.
        """
        ##        if self.__state not in (self.DISABLED, self.RUNNING):
        ##            self.__bad_transition(self.ENABLED)
        self.__state = self.ENABLED

    def one_shot(self, aProcess, aThread):
        """
        Transition to L{ONESHOT} state.
          - Forced by user: Disabled S{->} OneShot

        @type  aProcess: L{Process}
        @param aProcess: Process object.

        @type  aThread: L{Thread}
        @param aThread: Thread object.
        """
        ##        if self.__state != self.DISABLED:
        ##            self.__bad_transition(self.ONESHOT)
        self.__state = self.ONESHOT

    def running(self, aProcess, aThread):
        """
        Transition to L{RUNNING} state.
          - When hit: Enabled S{->} Running

        @type  aProcess: L{Process}
        @param aProcess: Process object.

        @type  aThread: L{Thread}
        @param aThread: Thread object.
        """
        if self.__state != self.ENABLED:
            self.__bad_transition(self.RUNNING)
        self.__state = self.RUNNING

    def hit(self, event):
        """
        Notify a breakpoint that it's been hit.

        This triggers the corresponding state transition and sets the
        C{breakpoint} property of the given L{Event} object.

        @see: L{disable}, L{enable}, L{one_shot}, L{running}

        @type  event: L{Event}
```
