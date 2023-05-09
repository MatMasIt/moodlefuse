# -*- coding: utf-8 -*-

"""

REFUSE
Simple cross-plattform ctypes bindings for libfuse / FUSE for macOS / WinFsp
https://github.com/pleiszenburg/refuse

    src/refuse/_refactor.py: Temporary helper for code refactoring

    THIS FILE IS TEMPORARY AND WILL BE REMOVED!

    Copyright (C) 2008-2020 refuse contributors

<LICENSE_BLOCK>
The contents of this file are subject to the Internet Systems Consortium (ISC)
license ("ISC license" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/ISC
https://github.com/pleiszenburg/refuse/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import ctypes
from ctypes.util import find_library
import sys

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# FIND LIBRARY
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_libfuse(_system):

    _libfuse_path = os.environ.get('FUSE_LIBRARY_PATH')
    if not _libfuse_path:
        if _system == 'Darwin':
            # libfuse dependency
            _libiconv = ctypes.CDLL(find_library('iconv'), ctypes.RTLD_GLOBAL)

            _libfuse_path = (find_library('fuse4x') or find_library('osxfuse') or
                             find_library('fuse'))
        elif _system == 'Windows':
            try:
                import _winreg as reg
            except ImportError:
                import winreg as reg
            def Reg32GetValue(rootkey, keyname, valname):
                key, val = None, None
                try:
                    key = reg.OpenKey(rootkey, keyname, 0, reg.KEY_READ | reg.KEY_WOW64_32KEY)
                    val = str(reg.QueryValueEx(key, valname)[0])
                except WindowsError:
                    pass
                finally:
                    if key is not None:
                        reg.CloseKey(key)
                return val
            _libfuse_path = Reg32GetValue(reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WinFsp", r"InstallDir")
            if _libfuse_path:
                _libfuse_path += r"bin\winfsp-%s.dll" % ("x64" if sys.maxsize > 0xffffffff else "x86")
        else:
            _libfuse_path = find_library('fuse')

    if not _libfuse_path:
        raise EnvironmentError('Unable to find libfuse')
    else:
        _libfuse = ctypes.CDLL(_libfuse_path)

    return _libfuse
