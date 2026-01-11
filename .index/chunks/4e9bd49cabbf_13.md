# Chunk: 4e9bd49cabbf_13

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 1030-1105
- chunk: 14/64

```
ecture specific implementation.
    def __new__(cls, *argv, **argd):
        try:
            arch = argd["arch"]
            del argd["arch"]
        except KeyError:
            try:
                arch = argv[4]
                argv = argv[:4] + argv[5:]
            except IndexError:
                raise TypeError("Missing 'arch' argument!")
        if arch is None:
            arch = win32.arch
        if arch == win32.ARCH_I386:
            return _Hook_i386(*argv, **argd)
        if arch == win32.ARCH_AMD64:
            return _Hook_amd64(*argv, **argd)
        return object.__new__(cls, *argv, **argd)

    # XXX FIXME
    #
    # Hardware breakpoints don't work correctly (or al all) in old VirtualBox
    # versions (3.0 and below).
    #
    # Maybe there should be a way to autodetect the buggy VirtualBox versions
    # and tell Hook objects not to use hardware breakpoints?
    #
    # For now the workaround is to manually set this variable to True when
    # WinAppDbg is installed on a physical machine.
    #
    useHardwareBreakpoints = False

    def __init__(self, preCB=None, postCB=None, paramCount=None, signature=None, arch=None):
        """
        @type  preCB: function
        @param preCB: (Optional) Callback triggered on function entry.

            The signature for the callback should be something like this::

                def pre_LoadLibraryEx(event, ra, lpFilename, hFile, dwFlags):

                    # return address
                    ra = params[0]

                    # function arguments start from here...
                    szFilename = event.get_process().peek_string(lpFilename)

                    # (...)

            Note that all pointer types are treated like void pointers, so your
            callback won't get the string or structure pointed to by it, but
            the remote memory address instead. This is so to prevent the ctypes
            library from being "too helpful" and trying to dereference the
            pointer. To get the actual data being pointed to, use one of the
            L{Process.read} methods.

        @type  postCB: function
        @param postCB: (Optional) Callback triggered on function exit.

            The signature for the callback should be something like this::

                def post_LoadLibraryEx(event, return_value):

                    # (...)

        @type  paramCount: int
        @param paramCount:
            (Optional) Number of parameters for the C{preCB} callback,
            not counting the return address. Parameters are read from
            the stack and assumed to be DWORDs in 32 bits and QWORDs in 64.

            This is a faster way to pull stack parameters in 32 bits, but in 64
            bits (or with some odd APIs in 32 bits) it won't be useful, since
            not all arguments to the hooked function will be of the same size.

```
