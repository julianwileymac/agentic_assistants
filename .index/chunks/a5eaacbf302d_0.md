# Chunk: a5eaacbf302d_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/win32/version.py`
- lines: 1-77
- chunk: 1/13

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2009-2014, Mario Vilas
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice,this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
Detect the current architecture and operating system.

Some functions here are really from kernel32.dll, others from version.dll.
"""

__revision__ = "$Id$"

from winappdbg.win32.defines import *

# ==============================================================================
# This is used later on to calculate the list of exported symbols.
_all = None
_all = set(vars().keys())
# ==============================================================================

# --- NTDDI version ------------------------------------------------------------

NTDDI_WIN8 = 0x06020000
NTDDI_WIN7SP1 = 0x06010100
NTDDI_WIN7 = 0x06010000
NTDDI_WS08 = 0x06000100
NTDDI_VISTASP1 = 0x06000100
NTDDI_VISTA = 0x06000000
NTDDI_LONGHORN = NTDDI_VISTA
NTDDI_WS03SP2 = 0x05020200
NTDDI_WS03SP1 = 0x05020100
NTDDI_WS03 = 0x05020000
NTDDI_WINXPSP3 = 0x05010300
NTDDI_WINXPSP2 = 0x05010200
NTDDI_WINXPSP1 = 0x05010100
NTDDI_WINXP = 0x05010000
NTDDI_WIN2KSP4 = 0x05000400
NTDDI_WIN2KSP3 = 0x05000300
NTDDI_WIN2KSP2 = 0x05000200
NTDDI_WIN2KSP1 = 0x05000100
NTDDI_WIN2K = 0x05000000
NTDDI_WINNT4 = 0x04000000

OSVERSION_MASK = 0xFFFF0000
SPVERSION_MASK = 0x0000FF00
SUBVERSION_MASK = 0x000000FF

# --- OSVERSIONINFO and OSVERSIONINFOEX structures and constants ---------------

VER_PLATFORM_WIN32s = 0
```
