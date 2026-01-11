# Chunk: 4e9bd49cabbf_2

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 165-264
- chunk: 3/64

```
vent} object,
            and the return value is a boolean
            (C{True} to dispatch the event, C{False} otherwise).

        @type  action: function
        @param action: (Optional) Action callback function.
            If specified, the event is handled by this callback instead of
            being dispatched normally.

            The callback signature is::

                def action_callback(event):
                    pass        # no return value

            Where B{event} is an L{Event} object.
        """
        self.__address = address
        self.__size = size
        self.__state = self.DISABLED

        self.set_condition(condition)
        self.set_action(action)

    def __repr__(self):
        if self.is_disabled():
            state = "Disabled"
        else:
            state = "Active (%s)" % self.get_state_name()
        if self.is_conditional():
            condition = "conditional"
        else:
            condition = "unconditional"
        name = self.typeName
        size = self.get_size()
        if size == 1:
            address = HexDump.address(self.get_address())
        else:
            begin = self.get_address()
            end = begin + size
            begin = HexDump.address(begin)
            end = HexDump.address(end)
            address = "range %s-%s" % (begin, end)
        msg = "<%s %s %s at remote address %s>"
        msg = msg % (state, condition, name, address)
        return msg

    # ------------------------------------------------------------------------------

    def is_disabled(self):
        """
        @rtype:  bool
        @return: C{True} if the breakpoint is in L{DISABLED} state.
        """
        return self.get_state() == self.DISABLED

    def is_enabled(self):
        """
        @rtype:  bool
        @return: C{True} if the breakpoint is in L{ENABLED} state.
        """
        return self.get_state() == self.ENABLED

    def is_one_shot(self):
        """
        @rtype:  bool
        @return: C{True} if the breakpoint is in L{ONESHOT} state.
        """
        return self.get_state() == self.ONESHOT

    def is_running(self):
        """
        @rtype:  bool
        @return: C{True} if the breakpoint is in L{RUNNING} state.
        """
        return self.get_state() == self.RUNNING

    def is_here(self, address):
        """
        @rtype:  bool
        @return: C{True} if the address is within the range of the breakpoint.
        """
        begin = self.get_address()
        end = begin + self.get_size()
        return begin <= address < end

    def get_address(self):
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

```
