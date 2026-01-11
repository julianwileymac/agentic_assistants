# Chunk: 4e9bd49cabbf_4

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 339-426
- chunk: 5/64

```
alse} otherwise.
        """
        condition = self.get_condition()
        if condition is True:  # shortcut for unconditional breakpoints
            return True
        if callable(condition):
            try:
                return bool(condition(event))
            except Exception:
                e = sys.exc_info()[1]
                msg = "Breakpoint condition callback %r" " raised an exception: %s"
                msg = msg % (condition, traceback.format_exc(e))
                warnings.warn(msg, BreakpointCallbackWarning)
                return False
        return bool(condition)  # force evaluation now

    # ------------------------------------------------------------------------------

    def is_automatic(self):
        """
        @rtype:  bool
        @return: C{True} if the breakpoint has an action callback defined.
        """
        return self.__action is not None

    def is_interactive(self):
        """
        @rtype:  bool
        @return:
            C{True} if the breakpoint doesn't have an action callback defined.
        """
        return self.__action is None

    def get_action(self):
        """
        @rtype:  bool, function
        @return: Returns the action callback for automatic breakpoints.
            Returns C{None} for interactive breakpoints.
        """
        return self.__action

    def set_action(self, action=None):
        """
        Sets a new action callback for the breakpoint.

        @type  action: function
        @param action: (Optional) Action callback function.
        """
        self.__action = action

    def run_action(self, event):
        """
        Executes the breakpoint action callback, if any was set.

        @type  event: L{Event}
        @param event: Debug event triggered by the breakpoint.
        """
        action = self.get_action()
        if action is not None:
            try:
                return bool(action(event))
            except Exception:
                e = sys.exc_info()[1]
                msg = "Breakpoint action callback %r" " raised an exception: %s"
                msg = msg % (action, traceback.format_exc(e))
                warnings.warn(msg, BreakpointCallbackWarning)
                return False
        return True

    # ------------------------------------------------------------------------------

    def __bad_transition(self, state):
        """
        Raises an C{AssertionError} exception for an invalid state transition.

        @see: L{stateNames}

        @type  state: int
        @param state: Intended breakpoint state.

        @raise Exception: Always.
        """
        statemsg = ""
        oldState = self.stateNames[self.get_state()]
        newState = self.stateNames[state]
        msg = "Invalid state transition (%s -> %s)" " for breakpoint at address %s"
        msg = msg % (oldState, newState, HexDump.address(self.get_address()))
```
