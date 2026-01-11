# Chunk: 4e9bd49cabbf_0

- source: `.venv-lab/Lib/site-packages/debugpy/_vendored/pydevd/pydevd_attach_to_process/winappdbg/breakpoint.py`
- lines: 1-88
- chunk: 1/64

```
#!~/.wine/drive_c/Python25/python.exe
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
Breakpoints.

@group Breakpoints:
    Breakpoint, CodeBreakpoint, PageBreakpoint, HardwareBreakpoint,
    BufferWatch, Hook, ApiHook

@group Warnings:
    BreakpointWarning, BreakpointCallbackWarning
"""

__revision__ = "$Id$"

__all__ = [
    # Base class for breakpoints
    "Breakpoint",
    # Breakpoint implementations
    "CodeBreakpoint",
    "PageBreakpoint",
    "HardwareBreakpoint",
    # Hooks and watches
    "Hook",
    "ApiHook",
    "BufferWatch",
    # Warnings
    "BreakpointWarning",
    "BreakpointCallbackWarning",
]

from winappdbg import win32
from winappdbg import compat
import sys
from winappdbg.process import Process, Thread
from winappdbg.util import DebugRegister, MemoryAddresses
from winappdbg.textio import HexDump

import ctypes
import warnings
import traceback

# ==============================================================================


class BreakpointWarning(UserWarning):
    """
    This warning is issued when a non-fatal error occurs that's related to
    breakpoints.
    """


class BreakpointCallbackWarning(RuntimeWarning):
    """
    This warning is issued when an uncaught exception was raised by a
    breakpoint's user-defined callback.
    """


```
