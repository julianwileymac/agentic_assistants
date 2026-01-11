# Chunk: a5eaacbf302d_10

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/version.py`
- lines: 836-924
- chunk: 11/13

```
(SM_SERVERR2):
                    if bits == 64 or wow64:
                        return "Windows 2003 R2 (64 bits)"
                    return "Windows 2003 R2"
                if osvi.wSuiteMask in (VER_SUITE_STORAGE_SERVER, VER_SUITE_WH_SERVER):
                    if bits == 64 or wow64:
                        return "Windows 2003 (64 bits)"
                    return "Windows 2003"
                if osvi.wProductType == VER_NT_WORKSTATION and arch == ARCH_AMD64:
                    return "Windows XP (64 bits)"
                else:
                    if bits == 64 or wow64:
                        return "Windows 2003 (64 bits)"
                    return "Windows 2003"
            if osvi.dwMinorVersion == 1:
                return "Windows XP"
            if osvi.dwMinorVersion == 0:
                return "Windows 2000"
        if osvi.dwMajorVersion == 4:
            return "Windows NT"
    return "Unknown"


def _get_ntddi(osvi):
    """
    Determines the current operating system.

    This function allows you to quickly tell apart major OS differences.
    For more detailed information call L{kernel32.GetVersionEx} instead.

    @note:
        Wine reports itself as Windows XP 32 bits
        (even if the Linux host is 64 bits).
        ReactOS may report itself as Windows 2000 or Windows XP,
        depending on the version of ReactOS.

    @type  osvi: L{OSVERSIONINFOEXA}
    @param osvi: Optional. The return value from L{kernel32.GetVersionEx}.

    @rtype:  int
    @return: NTDDI version number.
    """
    if not osvi:
        osvi = GetVersionEx()
    ntddi = 0
    ntddi += (osvi.dwMajorVersion & 0xFF) << 24
    ntddi += (osvi.dwMinorVersion & 0xFF) << 16
    ntddi += (osvi.wServicePackMajor & 0xFF) << 8
    ntddi += osvi.wServicePackMinor & 0xFF
    return ntddi


# The order of the following definitions DOES matter!

# Current integer size in bits. See L{_get_bits} for more details.
bits = _get_bits()

# Current processor architecture. See L{_get_arch} for more details.
arch = _get_arch()

# Set to C{True} if the current process is running in WOW64. See L{_get_wow64} for more details.
wow64 = _get_wow64()

_osvi = GetVersionEx()

# Current operating system. See L{_get_os} for more details.
os = _get_os(_osvi)

# Current operating system as an NTDDI constant. See L{_get_ntddi} for more details.
NTDDI_VERSION = _get_ntddi(_osvi)

# Upper word of L{NTDDI_VERSION}, contains the OS major and minor version number.
WINVER = NTDDI_VERSION >> 16

# --- version.dll --------------------------------------------------------------

VS_FF_DEBUG = 0x00000001
VS_FF_PRERELEASE = 0x00000002
VS_FF_PATCHED = 0x00000004
VS_FF_PRIVATEBUILD = 0x00000008
VS_FF_INFOINFERRED = 0x00000010
VS_FF_SPECIALBUILD = 0x00000020

VOS_UNKNOWN = 0x00000000
VOS__WINDOWS16 = 0x00000001
VOS__PM16 = 0x00000002
VOS__PM32 = 0x00000003
VOS__WINDOWS32 = 0x00000004
```
