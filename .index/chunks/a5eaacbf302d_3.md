# Chunk: a5eaacbf302d_3

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/version.py`
- lines: 277-362
- chunk: 4/13

```
CYMENUCHECK = 72
SM_SLOWMACHINE = 73
SM_MIDEASTENABLED = 74
SM_MOUSEWHEELPRESENT = 75
SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79
SM_CMONITORS = 80
SM_SAMEDISPLAYFORMAT = 81
SM_IMMENABLED = 82
SM_CXFOCUSBORDER = 83
SM_CYFOCUSBORDER = 84
SM_TABLETPC = 86
SM_MEDIACENTER = 87
SM_STARTER = 88
SM_SERVERR2 = 89
SM_MOUSEHORIZONTALWHEELPRESENT = 91
SM_CXPADDEDBORDER = 92

SM_CMETRICS = 93

SM_REMOTESESSION = 0x1000
SM_SHUTTINGDOWN = 0x2000
SM_REMOTECONTROL = 0x2001
SM_CARETBLINKINGENABLED = 0x2002

# --- SYSTEM_INFO structure, GetSystemInfo() and GetNativeSystemInfo() ---------

# Values used by Wine
# Documented values at MSDN are marked with an asterisk
PROCESSOR_ARCHITECTURE_UNKNOWN = 0xFFFF  # Unknown architecture.
PROCESSOR_ARCHITECTURE_INTEL = 0  # x86 (AMD or Intel) *
PROCESSOR_ARCHITECTURE_MIPS = 1  # MIPS
PROCESSOR_ARCHITECTURE_ALPHA = 2  # Alpha
PROCESSOR_ARCHITECTURE_PPC = 3  # Power PC
PROCESSOR_ARCHITECTURE_SHX = 4  # SHX
PROCESSOR_ARCHITECTURE_ARM = 5  # ARM
PROCESSOR_ARCHITECTURE_IA64 = 6  # Intel Itanium *
PROCESSOR_ARCHITECTURE_ALPHA64 = 7  # Alpha64
PROCESSOR_ARCHITECTURE_MSIL = 8  # MSIL
PROCESSOR_ARCHITECTURE_AMD64 = 9  # x64 (AMD or Intel) *
PROCESSOR_ARCHITECTURE_IA32_ON_WIN64 = 10  # IA32 on Win64
PROCESSOR_ARCHITECTURE_SPARC = 20  # Sparc (Wine)

# Values used by Wine
# PROCESSOR_OPTIL value found at http://code.google.com/p/ddab-lib/
# Documented values at MSDN are marked with an asterisk
PROCESSOR_INTEL_386 = 386  # Intel i386 *
PROCESSOR_INTEL_486 = 486  # Intel i486 *
PROCESSOR_INTEL_PENTIUM = 586  # Intel Pentium *
PROCESSOR_INTEL_IA64 = 2200  # Intel IA64 (Itanium) *
PROCESSOR_AMD_X8664 = 8664  # AMD X86 64 *
PROCESSOR_MIPS_R4000 = 4000  # MIPS R4000, R4101, R3910
PROCESSOR_ALPHA_21064 = 21064  # Alpha 210 64
PROCESSOR_PPC_601 = 601  # PPC 601
PROCESSOR_PPC_603 = 603  # PPC 603
PROCESSOR_PPC_604 = 604  # PPC 604
PROCESSOR_PPC_620 = 620  # PPC 620
PROCESSOR_HITACHI_SH3 = 10003  # Hitachi SH3 (Windows CE)
PROCESSOR_HITACHI_SH3E = 10004  # Hitachi SH3E (Windows CE)
PROCESSOR_HITACHI_SH4 = 10005  # Hitachi SH4 (Windows CE)
PROCESSOR_MOTOROLA_821 = 821  # Motorola 821 (Windows CE)
PROCESSOR_SHx_SH3 = 103  # SHx SH3 (Windows CE)
PROCESSOR_SHx_SH4 = 104  # SHx SH4 (Windows CE)
PROCESSOR_STRONGARM = 2577  # StrongARM (Windows CE)
PROCESSOR_ARM720 = 1824  # ARM 720 (Windows CE)
PROCESSOR_ARM820 = 2080  # ARM 820 (Windows CE)
PROCESSOR_ARM920 = 2336  # ARM 920 (Windows CE)
PROCESSOR_ARM_7TDMI = 70001  # ARM 7TDMI (Windows CE)
PROCESSOR_OPTIL = 0x494F  # MSIL

# typedef struct _SYSTEM_INFO {
#   union {
#     DWORD dwOemId;
#     struct {
#       WORD wProcessorArchitecture;
#       WORD wReserved;
#     } ;
#   }     ;
#   DWORD     dwPageSize;
#   LPVOID    lpMinimumApplicationAddress;
#   LPVOID    lpMaximumApplicationAddress;
#   DWORD_PTR dwActiveProcessorMask;
#   DWORD     dwNumberOfProcessors;
```
