# Chunk: 4e9bd49cabbf_62

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 4650-4731
- chunk: 63/64

```
      for pid in self.get_debugee_pids():
            self.start_tracing_process(pid)

    def stop_tracing_all(self):
        """
        Stop tracing mode for all threads in all debugees.
        """
        for pid in self.get_debugee_pids():
            self.stop_tracing_process(pid)

    # ------------------------------------------------------------------------------

    # Break on LastError values (only available since Windows Server 2003)

    def break_on_error(self, pid, errorCode):
        """
        Sets or clears the system breakpoint for a given Win32 error code.

        Use L{Process.is_system_defined_breakpoint} to tell if a breakpoint
        exception was caused by a system breakpoint or by the application
        itself (for example because of a failed assertion in the code).

        @note: This functionality is only available since Windows Server 2003.
            In 2003 it only breaks on error values set externally to the
            kernel32.dll library, but this was fixed in Windows Vista.

        @warn: This method will fail if the debug symbols for ntdll (kernel32
            in Windows 2003) are not present. For more information see:
            L{System.fix_symbol_store_path}.

        @see: U{http://www.nynaeve.net/?p=147}

        @type  pid: int
        @param pid: Process ID.

        @type  errorCode: int
        @param errorCode: Win32 error code to stop on. Set to C{0} or
            C{ERROR_SUCCESS} to clear the breakpoint instead.

        @raise NotImplementedError:
            The functionality is not supported in this system.

        @raise WindowsError:
            An error occurred while processing this request.
        """
        aProcess = self.system.get_process(pid)
        address = aProcess.get_break_on_error_ptr()
        if not address:
            raise NotImplementedError("The functionality is not supported in this system.")
        aProcess.write_dword(address, errorCode)

    def dont_break_on_error(self, pid):
        """
        Alias to L{break_on_error}C{(pid, ERROR_SUCCESS)}.

        @type  pid: int
        @param pid: Process ID.

        @raise NotImplementedError:
            The functionality is not supported in this system.

        @raise WindowsError:
            An error occurred while processing this request.
        """
        self.break_on_error(pid, 0)

    # ------------------------------------------------------------------------------

    # Simplified symbol resolving, useful for hooking functions

    def resolve_exported_function(self, pid, modName, procName):
        """
        Resolves the exported DLL function for the given process.

        @type  pid: int
        @param pid: Process global ID.

        @type  modName: str
        @param modName: Name of the module that exports the function.

        @type  procName: str
```
