# Chunk: a5eaacbf302d_7

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/version.py`
- lines: 607-717
- chunk: 8/13

```
VerSetConditionMask
    _VerSetConditionMask.argtypes = [ULONGLONG, DWORD, BYTE]
    _VerSetConditionMask.restype = ULONGLONG
    return _VerSetConditionMask(dwlConditionMask, dwTypeBitMask, dwConditionMask)


# --- get_bits, get_arch and get_os --------------------------------------------

ARCH_UNKNOWN = "unknown"
ARCH_I386 = "i386"
ARCH_MIPS = "mips"
ARCH_ALPHA = "alpha"
ARCH_PPC = "ppc"
ARCH_SHX = "shx"
ARCH_ARM = "arm"
ARCH_ARM64 = "arm64"
ARCH_THUMB = "thumb"
ARCH_IA64 = "ia64"
ARCH_ALPHA64 = "alpha64"
ARCH_MSIL = "msil"
ARCH_AMD64 = "amd64"
ARCH_SPARC = "sparc"

# aliases
ARCH_IA32 = ARCH_I386
ARCH_X86 = ARCH_I386
ARCH_X64 = ARCH_AMD64
ARCH_ARM7 = ARCH_ARM
ARCH_ARM8 = ARCH_ARM64
ARCH_T32 = ARCH_THUMB
ARCH_AARCH32 = ARCH_ARM7
ARCH_AARCH64 = ARCH_ARM8
ARCH_POWERPC = ARCH_PPC
ARCH_HITACHI = ARCH_SHX
ARCH_ITANIUM = ARCH_IA64

# win32 constants -> our constants
_arch_map = {
    PROCESSOR_ARCHITECTURE_INTEL: ARCH_I386,
    PROCESSOR_ARCHITECTURE_MIPS: ARCH_MIPS,
    PROCESSOR_ARCHITECTURE_ALPHA: ARCH_ALPHA,
    PROCESSOR_ARCHITECTURE_PPC: ARCH_PPC,
    PROCESSOR_ARCHITECTURE_SHX: ARCH_SHX,
    PROCESSOR_ARCHITECTURE_ARM: ARCH_ARM,
    PROCESSOR_ARCHITECTURE_IA64: ARCH_IA64,
    PROCESSOR_ARCHITECTURE_ALPHA64: ARCH_ALPHA64,
    PROCESSOR_ARCHITECTURE_MSIL: ARCH_MSIL,
    PROCESSOR_ARCHITECTURE_AMD64: ARCH_AMD64,
    PROCESSOR_ARCHITECTURE_SPARC: ARCH_SPARC,
}

OS_UNKNOWN = "Unknown"
OS_NT = "Windows NT"
OS_W2K = "Windows 2000"
OS_XP = "Windows XP"
OS_XP_64 = "Windows XP (64 bits)"
OS_W2K3 = "Windows 2003"
OS_W2K3_64 = "Windows 2003 (64 bits)"
OS_W2K3R2 = "Windows 2003 R2"
OS_W2K3R2_64 = "Windows 2003 R2 (64 bits)"
OS_W2K8 = "Windows 2008"
OS_W2K8_64 = "Windows 2008 (64 bits)"
OS_W2K8R2 = "Windows 2008 R2"
OS_W2K8R2_64 = "Windows 2008 R2 (64 bits)"
OS_VISTA = "Windows Vista"
OS_VISTA_64 = "Windows Vista (64 bits)"
OS_W7 = "Windows 7"
OS_W7_64 = "Windows 7 (64 bits)"

OS_SEVEN = OS_W7
OS_SEVEN_64 = OS_W7_64

OS_WINDOWS_NT = OS_NT
OS_WINDOWS_2000 = OS_W2K
OS_WINDOWS_XP = OS_XP
OS_WINDOWS_XP_64 = OS_XP_64
OS_WINDOWS_2003 = OS_W2K3
OS_WINDOWS_2003_64 = OS_W2K3_64
OS_WINDOWS_2003_R2 = OS_W2K3R2
OS_WINDOWS_2003_R2_64 = OS_W2K3R2_64
OS_WINDOWS_2008 = OS_W2K8
OS_WINDOWS_2008_64 = OS_W2K8_64
OS_WINDOWS_2008_R2 = OS_W2K8R2
OS_WINDOWS_2008_R2_64 = OS_W2K8R2_64
OS_WINDOWS_VISTA = OS_VISTA
OS_WINDOWS_VISTA_64 = OS_VISTA_64
OS_WINDOWS_SEVEN = OS_W7
OS_WINDOWS_SEVEN_64 = OS_W7_64


def _get_bits():
    """
    Determines the current integer size in bits.

    This is useful to know if we're running in a 32 bits or a 64 bits machine.

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

```
