# Chunk: 4e9bd49cabbf_21

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 1623-1710
- chunk: 22/64

```
  not counting the return address. Parameters are read from
            the stack and assumed to be DWORDs in 32 bits and QWORDs in 64.

            This is a faster way to pull stack parameters in 32 bits, but in 64
            bits (or with some odd APIs in 32 bits) it won't be useful, since
            not all arguments to the hooked function will be of the same size.

            For a more reliable and cross-platform way of hooking use the
            C{signature} argument instead.

        @type  signature: tuple
        @param signature:
            (Optional) Tuple of C{ctypes} data types that constitute the
            hooked function signature. When the function is called, this will
            be used to parse the arguments from the stack. Overrides the
            C{paramCount} argument.
        """
        self.__modName = modName
        self.__procName = procName
        self.__paramCount = paramCount
        self.__signature = signature
        self.__preCB = getattr(eventHandler, "pre_%s" % procName, None)
        self.__postCB = getattr(eventHandler, "post_%s" % procName, None)
        self.__hook = dict()

    def __call__(self, event):
        """
        Handles the breakpoint event on entry of the function.

        @type  event: L{ExceptionEvent}
        @param event: Breakpoint hit event.

        @raise WindowsError: An error occured.
        """
        pid = event.get_pid()
        try:
            hook = self.__hook[pid]
        except KeyError:
            hook = Hook(self.__preCB, self.__postCB, self.__paramCount, self.__signature, event.get_process().get_arch())
            self.__hook[pid] = hook
        return hook(event)

    @property
    def modName(self):
        return self.__modName

    @property
    def procName(self):
        return self.__procName

    def hook(self, debug, pid):
        """
        Installs the API hook on a given process and module.

        @warning: Do not call from an API hook callback.

        @type  debug: L{Debug}
        @param debug: Debug object.

        @type  pid: int
        @param pid: Process ID.
        """
        label = "%s!%s" % (self.__modName, self.__procName)
        try:
            hook = self.__hook[pid]
        except KeyError:
            try:
                aProcess = debug.system.get_process(pid)
            except KeyError:
                aProcess = Process(pid)
            hook = Hook(self.__preCB, self.__postCB, self.__paramCount, self.__signature, aProcess.get_arch())
            self.__hook[pid] = hook
        hook.hook(debug, pid, label)

    def unhook(self, debug, pid):
        """
        Removes the API hook from the given process and module.

        @warning: Do not call from an API hook callback.

        @type  debug: L{Debug}
        @param debug: Debug object.

        @type  pid: int
        @param pid: Process ID.
        """
        try:
```
