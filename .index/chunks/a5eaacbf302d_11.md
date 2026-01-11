# Chunk: a5eaacbf302d_11

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/version.py`
- lines: 912-1019
- chunk: 12/13

```
000001
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
VOS_DOS = 0x00010000
VOS_OS216 = 0x00020000
VOS_OS232 = 0x00030000
VOS_NT = 0x00040000

VOS_DOS_WINDOWS16 = 0x00010001
VOS_DOS_WINDOWS32 = 0x00010004
VOS_NT_WINDOWS32 = 0x00040004
VOS_OS216_PM16 = 0x00020002
VOS_OS232_PM32 = 0x00030003

VFT_UNKNOWN = 0x00000000
VFT_APP = 0x00000001
VFT_DLL = 0x00000002
VFT_DRV = 0x00000003
VFT_FONT = 0x00000004
VFT_VXD = 0x00000005
VFT_RESERVED = 0x00000006  # undocumented
VFT_STATIC_LIB = 0x00000007

VFT2_UNKNOWN = 0x00000000

VFT2_DRV_PRINTER = 0x00000001
VFT2_DRV_KEYBOARD = 0x00000002
VFT2_DRV_LANGUAGE = 0x00000003
VFT2_DRV_DISPLAY = 0x00000004
VFT2_DRV_MOUSE = 0x00000005
VFT2_DRV_NETWORK = 0x00000006
VFT2_DRV_SYSTEM = 0x00000007
VFT2_DRV_INSTALLABLE = 0x00000008
VFT2_DRV_SOUND = 0x00000009
VFT2_DRV_COMM = 0x0000000A
VFT2_DRV_RESERVED = 0x0000000B  # undocumented
VFT2_DRV_VERSIONED_PRINTER = 0x0000000C

VFT2_FONT_RASTER = 0x00000001
VFT2_FONT_VECTOR = 0x00000002
VFT2_FONT_TRUETYPE = 0x00000003


# typedef struct tagVS_FIXEDFILEINFO {
#   DWORD dwSignature;
#   DWORD dwStrucVersion;
#   DWORD dwFileVersionMS;
#   DWORD dwFileVersionLS;
#   DWORD dwProductVersionMS;
#   DWORD dwProductVersionLS;
#   DWORD dwFileFlagsMask;
#   DWORD dwFileFlags;
#   DWORD dwFileOS;
#   DWORD dwFileType;
#   DWORD dwFileSubtype;
#   DWORD dwFileDateMS;
#   DWORD dwFileDateLS;
# } VS_FIXEDFILEINFO;
class VS_FIXEDFILEINFO(Structure):
    _fields_ = [
        ("dwSignature", DWORD),
        ("dwStrucVersion", DWORD),
        ("dwFileVersionMS", DWORD),
        ("dwFileVersionLS", DWORD),
        ("dwProductVersionMS", DWORD),
        ("dwProductVersionLS", DWORD),
        ("dwFileFlagsMask", DWORD),
        ("dwFileFlags", DWORD),
        ("dwFileOS", DWORD),
        ("dwFileType", DWORD),
        ("dwFileSubtype", DWORD),
        ("dwFileDateMS", DWORD),
        ("dwFileDateLS", DWORD),
    ]


PVS_FIXEDFILEINFO = POINTER(VS_FIXEDFILEINFO)
LPVS_FIXEDFILEINFO = PVS_FIXEDFILEINFO


# BOOL WINAPI GetFileVersionInfo(
#   _In_        LPCTSTR lptstrFilename,
#   _Reserved_  DWORD dwHandle,
#   _In_        DWORD dwLen,
#   _Out_       LPVOID lpData
# );
# DWORD WINAPI GetFileVersionInfoSize(
#   _In_       LPCTSTR lptstrFilename,
#   _Out_opt_  LPDWORD lpdwHandle
# );
def GetFileVersionInfoA(lptstrFilename):
    _GetFileVersionInfoA = windll.version.GetFileVersionInfoA
    _GetFileVersionInfoA.argtypes = [LPSTR, DWORD, DWORD, LPVOID]
    _GetFileVersionInfoA.restype = bool
    _GetFileVersionInfoA.errcheck = RaiseIfZero

    _GetFileVersionInfoSizeA = windll.version.GetFileVersionInfoSizeA
    _GetFileVersionInfoSizeA.argtypes = [LPSTR, LPVOID]
```
