# Chunk: a5eaacbf302d_1

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/version.py`
- lines: 65-177
- chunk: 2/13

```
P2 = 0x05000200
NTDDI_WIN2KSP1 = 0x05000100
NTDDI_WIN2K = 0x05000000
NTDDI_WINNT4 = 0x04000000

OSVERSION_MASK = 0xFFFF0000
SPVERSION_MASK = 0x0000FF00
SUBVERSION_MASK = 0x000000FF

# --- OSVERSIONINFO and OSVERSIONINFOEX structures and constants ---------------

VER_PLATFORM_WIN32s = 0
VER_PLATFORM_WIN32_WINDOWS = 1
VER_PLATFORM_WIN32_NT = 2

VER_SUITE_BACKOFFICE = 0x00000004
VER_SUITE_BLADE = 0x00000400
VER_SUITE_COMPUTE_SERVER = 0x00004000
VER_SUITE_DATACENTER = 0x00000080
VER_SUITE_ENTERPRISE = 0x00000002
VER_SUITE_EMBEDDEDNT = 0x00000040
VER_SUITE_PERSONAL = 0x00000200
VER_SUITE_SINGLEUSERTS = 0x00000100
VER_SUITE_SMALLBUSINESS = 0x00000001
VER_SUITE_SMALLBUSINESS_RESTRICTED = 0x00000020
VER_SUITE_STORAGE_SERVER = 0x00002000
VER_SUITE_TERMINAL = 0x00000010
VER_SUITE_WH_SERVER = 0x00008000

VER_NT_DOMAIN_CONTROLLER = 0x0000002
VER_NT_SERVER = 0x0000003
VER_NT_WORKSTATION = 0x0000001

VER_BUILDNUMBER = 0x0000004
VER_MAJORVERSION = 0x0000002
VER_MINORVERSION = 0x0000001
VER_PLATFORMID = 0x0000008
VER_PRODUCT_TYPE = 0x0000080
VER_SERVICEPACKMAJOR = 0x0000020
VER_SERVICEPACKMINOR = 0x0000010
VER_SUITENAME = 0x0000040

VER_EQUAL = 1
VER_GREATER = 2
VER_GREATER_EQUAL = 3
VER_LESS = 4
VER_LESS_EQUAL = 5
VER_AND = 6
VER_OR = 7


# typedef struct _OSVERSIONINFO {
#   DWORD dwOSVersionInfoSize;
#   DWORD dwMajorVersion;
#   DWORD dwMinorVersion;
#   DWORD dwBuildNumber;
#   DWORD dwPlatformId;
#   TCHAR szCSDVersion[128];
# }OSVERSIONINFO;
class OSVERSIONINFOA(Structure):
    _fields_ = [
        ("dwOSVersionInfoSize", DWORD),
        ("dwMajorVersion", DWORD),
        ("dwMinorVersion", DWORD),
        ("dwBuildNumber", DWORD),
        ("dwPlatformId", DWORD),
        ("szCSDVersion", CHAR * 128),
    ]


class OSVERSIONINFOW(Structure):
    _fields_ = [
        ("dwOSVersionInfoSize", DWORD),
        ("dwMajorVersion", DWORD),
        ("dwMinorVersion", DWORD),
        ("dwBuildNumber", DWORD),
        ("dwPlatformId", DWORD),
        ("szCSDVersion", WCHAR * 128),
    ]


# typedef struct _OSVERSIONINFOEX {
#   DWORD dwOSVersionInfoSize;
#   DWORD dwMajorVersion;
#   DWORD dwMinorVersion;
#   DWORD dwBuildNumber;
#   DWORD dwPlatformId;
#   TCHAR szCSDVersion[128];
#   WORD  wServicePackMajor;
#   WORD  wServicePackMinor;
#   WORD  wSuiteMask;
#   BYTE  wProductType;
#   BYTE  wReserved;
# }OSVERSIONINFOEX, *POSVERSIONINFOEX, *LPOSVERSIONINFOEX;
class OSVERSIONINFOEXA(Structure):
    _fields_ = [
        ("dwOSVersionInfoSize", DWORD),
        ("dwMajorVersion", DWORD),
        ("dwMinorVersion", DWORD),
        ("dwBuildNumber", DWORD),
        ("dwPlatformId", DWORD),
        ("szCSDVersion", CHAR * 128),
        ("wServicePackMajor", WORD),
        ("wServicePackMinor", WORD),
        ("wSuiteMask", WORD),
        ("wProductType", BYTE),
        ("wReserved", BYTE),
    ]


class OSVERSIONINFOEXW(Structure):
    _fields_ = [
```
