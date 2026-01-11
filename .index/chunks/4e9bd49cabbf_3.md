# Chunk: 4e9bd49cabbf_3

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 251-348
- chunk: 4/64

```
     """
        @rtype:  int
        @return: The target memory address for the breakpoint.
        """
        return self.__address

    def get_size(self):
        """
        @rtype:  int
        @return: The size in bytes of the breakpoint.
        """
        return self.__size

    def get_span(self):
        """
        @rtype:  tuple( int, int )
        @return:
            Starting and ending address of the memory range
            covered by the breakpoint.
        """
        address = self.get_address()
        size = self.get_size()
        return (address, address + size)

    def get_state(self):
        """
        @rtype:  int
        @return: The current state of the breakpoint
            (L{DISABLED}, L{ENABLED}, L{ONESHOT}, L{RUNNING}).
        """
        return self.__state

    def get_state_name(self):
        """
        @rtype:  str
        @return: The name of the current state of the breakpoint.
        """
        return self.stateNames[self.get_state()]

    # ------------------------------------------------------------------------------

    def is_conditional(self):
        """
        @see: L{__init__}
        @rtype:  bool
        @return: C{True} if the breakpoint has a condition callback defined.
        """
        # Do not evaluate as boolean! Test for identity with True instead.
        return self.__condition is not True

    def is_unconditional(self):
        """
        @rtype:  bool
        @return: C{True} if the breakpoint doesn't have a condition callback defined.
        """
        # Do not evaluate as boolean! Test for identity with True instead.
        return self.__condition is True

    def get_condition(self):
        """
        @rtype:  bool, function
        @return: Returns the condition callback for conditional breakpoints.
            Returns C{True} for unconditional breakpoints.
        """
        return self.__condition

    def set_condition(self, condition=True):
        """
        Sets a new condition callback for the breakpoint.

        @see: L{__init__}

        @type  condition: function
        @param condition: (Optional) Condition callback function.
        """
        if condition is None:
            self.__condition = True
        else:
            self.__condition = condition

    def eval_condition(self, event):
        """
        Evaluates the breakpoint condition, if any was set.

        @type  event: L{Event}
        @param event: Debug event triggered by the breakpoint.

        @rtype:  bool
        @return: C{True} to dispatch the event, C{False} otherwise.
        """
        condition = self.get_condition()
        if condition is True:  # shortcut for unconditional breakpoints
            return True
        if callable(condition):
            try:
                return bool(condition(event))
            except Exception:
```
