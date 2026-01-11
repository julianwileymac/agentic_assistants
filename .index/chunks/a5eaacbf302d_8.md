# Chunk: a5eaacbf302d_8

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/version.py`
- lines: 701-783
- chunk: 9/13

```
nning in a 32 bits or a 64 bits machine.

    @rtype: int
    @return: Returns the size of L{SIZE_T} in bits.
    """
    return sizeof(SIZE_T) * 8


def _get_arch():
    """
    Determines the current processor architecture.

    @rtype: str
    @return:
        On error, returns:

         - L{ARCH_UNKNOWN} (C{"unknown"}) meaning the architecture could not be detected or is not known to WinAppDbg.

        On success, returns one of the following values:

         - L{ARCH_I386} (C{"i386"}) for Intel 32-bit x86 processor or compatible.
         - L{ARCH_AMD64} (C{"amd64"}) for Intel 64-bit x86_64 processor or compatible.

        May also return one of the following values if you get both Python and
        WinAppDbg to work in such machines... let me know if you do! :)

         - L{ARCH_MIPS} (C{"mips"}) for MIPS compatible processors.
         - L{ARCH_ALPHA} (C{"alpha"}) for Alpha processors.
         - L{ARCH_PPC} (C{"ppc"}) for PowerPC compatible processors.
         - L{ARCH_SHX} (C{"shx"}) for Hitachi SH processors.
         - L{ARCH_ARM} (C{"arm"}) for ARM compatible processors.
         - L{ARCH_IA64} (C{"ia64"}) for Intel Itanium processor or compatible.
         - L{ARCH_ALPHA64} (C{"alpha64"}) for Alpha64 processors.
         - L{ARCH_MSIL} (C{"msil"}) for the .NET virtual machine.
         - L{ARCH_SPARC} (C{"sparc"}) for Sun Sparc processors.

        Probably IronPython returns C{ARCH_MSIL} but I haven't tried it. Python
        on Windows CE and Windows Mobile should return C{ARCH_ARM}. Python on
        Solaris using Wine would return C{ARCH_SPARC}. Python in an Itanium
        machine should return C{ARCH_IA64} both on Wine and proper Windows.
        All other values should only be returned on Linux using Wine.
    """
    try:
        si = GetNativeSystemInfo()
    except Exception:
        si = GetSystemInfo()
    try:
        return _arch_map[si.id.w.wProcessorArchitecture]
    except KeyError:
        return ARCH_UNKNOWN


def _get_wow64():
    """
    Determines if the current process is running in Windows-On-Windows 64 bits.

    @rtype:  bool
    @return: C{True} of the current process is a 32 bit program running in a
        64 bit version of Windows, C{False} if it's either a 32 bit program
        in a 32 bit Windows or a 64 bit program in a 64 bit Windows.
    """
    # Try to determine if the debugger itself is running on WOW64.
    # On error assume False.
    if bits == 64:
        wow64 = False
    else:
        try:
            wow64 = IsWow64Process(GetCurrentProcess())
        except Exception:
            wow64 = False
    return wow64


def _get_os(osvi=None):
    """
    Determines the current operating system.

    This function allows you to quickly tell apart major OS differences.
    For more detailed information call L{GetVersionEx} instead.

    @note:
        Wine reports itself as Windows XP 32 bits
```
