# -*- coding: utf-8 -*-

"""

REFUSE
Simple cross-plattform ctypes bindings for libfuse / FUSE for macOS / WinFsp
https://github.com/pleiszenburg/refuse

    src/refuse/_inventory.py: Temporary helper for code refactoring

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

import _ctypes
from pprint import pprint as pp
import platform # machine, system
import subprocess
import sys


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# LIBRARY HEADER "INVENTORY"
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_arch():
    """Get system name and generic, OS-independent machine name
    """

    system = platform.system()
    machine = platform.machine()

    if machine in ('i386', 'i486', 'i586', 'i686'):
        machine = 'x86'

    # On Windows, machine equals hardware - not os. We want os.
    if system == 'Windows':
        machine = 'x86_64' if sys.platform == 'win64' else 'x86'

    return system, machine


def get_archs():

    system_dict = {
        'Windows': ['x86', 'x86_64'],
        'CYGWIN': ['x86', 'x86_64'],
        'OpenBSD': ['x86', 'x86_64', 'mips', 'ppc', 'ppc64', 'ppc64le', 'aarch64'],
        'FreeBSD': ['x86', 'x86_64'],
        'Darwin': ['x86', 'x86_64', 'ppc', 'ppc64'],
        'Darwin-MacFuse': ['x86', 'x86_64', 'ppc', 'ppc64'],
        'Linux': ['x86', 'x86_64', 'mips', 'ppc', 'ppc64', 'ppc64le', 'aarch64'],
        }

    arch_list = []
    for system, machines in system_dict.items():
        for machine in machines:
            arch_list.append((system, machine))

    for system, machine in arch_list:
        yield system, machine


def _analyze_item_(item):

    item_type = type(item)
    item_type_name = getattr(item_type, '__name__')

    if item_type in (int, float, str, bytes, bool, list, dict, set, tuple): # basic python type
        return item_type.__name__, item

    if hasattr(item, '_fields_'): # ctypes struct
        fields = [[field[0], _analyze_item_(field[1])] for field in item._fields_]
        return ['ctypes struct', fields]

    if item_type_name == 'PyCSimpleType':
        return getattr(item, '__name__')

    if item_type_name == 'PyCFuncPtrType':
        try:
            return [
                'ctypes func',
                [_analyze_item_(field) for field in getattr(item, 'argtypes', [])],
                _analyze_item_(item.restype)
                ]
        except:
            return [
                'ctypes func', '?'
                ]

    return getattr(item, '__name__', '?'), type(item)


def dump_globals(globals_dict):

    header_dict = {
        name: _analyze_item_(globals_dict[name])
        for name in globals_dict.keys()
        if not name.startswith('_') and name not in (
            'sys', # import
            'ctypes', # import
            'get_arch', # infrastructure
            'dump_globals', # debug
            'extra_fields' # TMP from OpenBSD port
            )
        }
    pp(header_dict)


def dump_header():

    for system, machine in get_archs():

        sys.stdout.write('+++ %s / %s +++\n' % (system, machine))
        sys.stdout.flush()
        proc = subprocess.Popen(
            ['python3', '-m', 'refuse._high_header', system, machine],
            stdout = subprocess.PIPE, stderr = subprocess.PIPE
            )
        data = proc.communicate()
        sys.stderr.write(data[1].decode('utf-8'))
        sys.stderr.flush()
        sys.stdout.write(data[0].decode('utf-8'))
        sys.stdout.flush()


if __name__ == '__main__':
    dump_header()
