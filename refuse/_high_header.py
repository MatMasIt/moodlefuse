# -*- coding: utf-8 -*-

"""

REFUSE
Simple cross-plattform ctypes bindings for libfuse / FUSE for macOS / WinFsp
https://github.com/pleiszenburg/refuse

    src/refuse/_high_header.py: Temporary helper for code refactoring

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

import ctypes
import sys

from ._inventory import dump_globals, get_arch

if __name__ == '__main__': # DEBUG
    _system, _machine = sys.argv[1], sys.argv[2]
else: # REGULAR
    _system, _machine = get_arch()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# HEADER: TYPES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if _system == 'Windows':
    # NOTE:
    #
    # sizeof(long)==4 on Windows 32-bit and 64-bit
    # sizeof(long)==4 on Cygwin 32-bit and ==8 on Cygwin 64-bit
    #
    # We have to fix up c_long and c_ulong so that it matches the
    # Cygwin (and UNIX) sizes when run on Windows.
    import sys
    if sys.maxsize > 0xffffffff:
        c_win_long = ctypes.c_int64
        c_win_ulong = ctypes.c_uint64
    else:
        c_win_long = ctypes.c_int32
        c_win_ulong = ctypes.c_uint32

if _system == 'Windows' or _system == 'CYGWIN':
    class c_timespec(ctypes.Structure):
        _fields_ = [('tv_sec', c_win_long), ('tv_nsec', c_win_long)]
elif _system == 'OpenBSD':
    c_time_t = ctypes.c_int64
    class c_timespec(ctypes.Structure):
        _fields_ = [('tv_sec', c_time_t), ('tv_nsec', ctypes.c_long)]
else:
    class c_timespec(ctypes.Structure):
        _fields_ = [('tv_sec', ctypes.c_long), ('tv_nsec', ctypes.c_long)]

class c_utimbuf(ctypes.Structure):
    _fields_ = [('actime', c_timespec), ('modtime', c_timespec)]

class c_stat(ctypes.Structure):
    pass    # Platform dependent

if _system in ('Darwin', 'Darwin-MacFuse', 'FreeBSD'):
    ENOTSUP = 45

    c_dev_t = ctypes.c_int32
    c_fsblkcnt_t = ctypes.c_ulong
    c_fsfilcnt_t = ctypes.c_ulong
    c_gid_t = ctypes.c_uint32
    c_mode_t = ctypes.c_uint16
    c_off_t = ctypes.c_int64
    c_pid_t = ctypes.c_int32
    c_uid_t = ctypes.c_uint32
    setxattr_t = ctypes.CFUNCTYPE(
        ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_byte), ctypes.c_size_t, ctypes.c_int,
        ctypes.c_uint32)
    getxattr_t = ctypes.CFUNCTYPE(
        ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_byte),
        ctypes.c_size_t, ctypes.c_uint32)
    if _system == 'Darwin':
        c_stat._fields_ = [
            ('st_dev', c_dev_t),
            ('st_mode', c_mode_t),
            ('st_nlink', ctypes.c_uint16),
            ('st_ino', ctypes.c_uint64),
            ('st_uid', c_uid_t),
            ('st_gid', c_gid_t),
            ('st_rdev', c_dev_t),
            ('st_atimespec', c_timespec),
            ('st_mtimespec', c_timespec),
            ('st_ctimespec', c_timespec),
            ('st_birthtimespec', c_timespec),
            ('st_size', c_off_t),
            ('st_blocks', ctypes.c_int64),
            ('st_blksize', ctypes.c_int32),
            ('st_flags', ctypes.c_int32),
            ('st_gen', ctypes.c_int32),
            ('st_lspare', ctypes.c_int32),
            ('st_qspare', ctypes.c_int64)]
    else: # MacFuse, FreeBSD
        c_stat._fields_ = [
            ('st_dev', c_dev_t),
            ('st_ino', ctypes.c_uint32),
            ('st_mode', c_mode_t),
            ('st_nlink', ctypes.c_uint16),
            ('st_uid', c_uid_t),
            ('st_gid', c_gid_t),
            ('st_rdev', c_dev_t),
            ('st_atimespec', c_timespec),
            ('st_mtimespec', c_timespec),
            ('st_ctimespec', c_timespec),
            ('st_size', c_off_t),
            ('st_blocks', ctypes.c_int64),
            ('st_blksize', ctypes.c_int32)]
elif _system == 'Linux':
    ENOTSUP = 95

    c_dev_t = ctypes.c_ulonglong
    c_fsblkcnt_t = ctypes.c_ulonglong
    c_fsfilcnt_t = ctypes.c_ulonglong
    c_gid_t = ctypes.c_uint
    c_mode_t = ctypes.c_uint
    c_off_t = ctypes.c_longlong
    c_pid_t = ctypes.c_int
    c_uid_t = ctypes.c_uint
    setxattr_t = ctypes.CFUNCTYPE(
        ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_byte), ctypes.c_size_t, ctypes.c_int)

    getxattr_t = ctypes.CFUNCTYPE(
        ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_byte), ctypes.c_size_t)

    if _machine == 'x86_64':
        c_stat._fields_ = [
            ('st_dev', c_dev_t),
            ('st_ino', ctypes.c_ulong),
            ('st_nlink', ctypes.c_ulong),
            ('st_mode', c_mode_t),
            ('st_uid', c_uid_t),
            ('st_gid', c_gid_t),
            ('__pad0', ctypes.c_int),
            ('st_rdev', c_dev_t),
            ('st_size', c_off_t),
            ('st_blksize', ctypes.c_long),
            ('st_blocks', ctypes.c_long),
            ('st_atimespec', c_timespec),
            ('st_mtimespec', c_timespec),
            ('st_ctimespec', c_timespec)]
    elif _machine == 'mips':
        c_stat._fields_ = [
            ('st_dev', c_dev_t),
            ('__pad1_1', ctypes.c_ulong),
            ('__pad1_2', ctypes.c_ulong),
            ('__pad1_3', ctypes.c_ulong),
            ('st_ino', ctypes.c_ulong),
            ('st_mode', c_mode_t),
            ('st_nlink', ctypes.c_ulong),
            ('st_uid', c_uid_t),
            ('st_gid', c_gid_t),
            ('st_rdev', c_dev_t),
            ('__pad2_1', ctypes.c_ulong),
            ('__pad2_2', ctypes.c_ulong),
            ('st_size', c_off_t),
            ('__pad3', ctypes.c_ulong),
            ('st_atimespec', c_timespec),
            ('__pad4', ctypes.c_ulong),
            ('st_mtimespec', c_timespec),
            ('__pad5', ctypes.c_ulong),
            ('st_ctimespec', c_timespec),
            ('__pad6', ctypes.c_ulong),
            ('st_blksize', ctypes.c_long),
            ('st_blocks', ctypes.c_long),
            ('__pad7_1', ctypes.c_ulong),
            ('__pad7_2', ctypes.c_ulong),
            ('__pad7_3', ctypes.c_ulong),
            ('__pad7_4', ctypes.c_ulong),
            ('__pad7_5', ctypes.c_ulong),
            ('__pad7_6', ctypes.c_ulong),
            ('__pad7_7', ctypes.c_ulong),
            ('__pad7_8', ctypes.c_ulong),
            ('__pad7_9', ctypes.c_ulong),
            ('__pad7_10', ctypes.c_ulong),
            ('__pad7_11', ctypes.c_ulong),
            ('__pad7_12', ctypes.c_ulong),
            ('__pad7_13', ctypes.c_ulong),
            ('__pad7_14', ctypes.c_ulong)]
    elif _machine == 'ppc':
        c_stat._fields_ = [
            ('st_dev', c_dev_t),
            ('st_ino', ctypes.c_ulonglong),
            ('st_mode', c_mode_t),
            ('st_nlink', ctypes.c_uint),
            ('st_uid', c_uid_t),
            ('st_gid', c_gid_t),
            ('st_rdev', c_dev_t),
            ('__pad2', ctypes.c_ushort),
            ('st_size', c_off_t),
            ('st_blksize', ctypes.c_long),
            ('st_blocks', ctypes.c_longlong),
            ('st_atimespec', c_timespec),
            ('st_mtimespec', c_timespec),
            ('st_ctimespec', c_timespec)]
    elif _machine == 'ppc64' or _machine == 'ppc64le':
        c_stat._fields_ = [
            ('st_dev', c_dev_t),
            ('st_ino', ctypes.c_ulong),
            ('st_nlink', ctypes.c_ulong),
            ('st_mode', c_mode_t),
            ('st_uid', c_uid_t),
            ('st_gid', c_gid_t),
            ('__pad', ctypes.c_uint),
            ('st_rdev', c_dev_t),
            ('st_size', c_off_t),
            ('st_blksize', ctypes.c_long),
            ('st_blocks', ctypes.c_long),
            ('st_atimespec', c_timespec),
            ('st_mtimespec', c_timespec),
            ('st_ctimespec', c_timespec)]
    elif _machine == 'aarch64':
        c_stat._fields_ = [
            ('st_dev', c_dev_t),
            ('st_ino', ctypes.c_ulong),
            ('st_mode', c_mode_t),
            ('st_nlink', ctypes.c_uint),
            ('st_uid', c_uid_t),
            ('st_gid', c_gid_t),
            ('st_rdev', c_dev_t),
            ('__pad1', ctypes.c_ulong),
            ('st_size', c_off_t),
            ('st_blksize', ctypes.c_int),
            ('__pad2', ctypes.c_int),
            ('st_blocks', ctypes.c_long),
            ('st_atimespec', c_timespec),
            ('st_mtimespec', c_timespec),
            ('st_ctimespec', c_timespec)]
    else:
        # i686, use as fallback for everything else
        c_stat._fields_ = [
            ('st_dev', c_dev_t),
            ('__pad1', ctypes.c_ushort),
            ('__st_ino', ctypes.c_ulong),
            ('st_mode', c_mode_t),
            ('st_nlink', ctypes.c_uint),
            ('st_uid', c_uid_t),
            ('st_gid', c_gid_t),
            ('st_rdev', c_dev_t),
            ('__pad2', ctypes.c_ushort),
            ('st_size', c_off_t),
            ('st_blksize', ctypes.c_long),
            ('st_blocks', ctypes.c_longlong),
            ('st_atimespec', c_timespec),
            ('st_mtimespec', c_timespec),
            ('st_ctimespec', c_timespec),
            ('st_ino', ctypes.c_ulonglong)]
elif _system == 'Windows' or _system == 'CYGWIN':
    ENOTSUP = 129 if _system == 'Windows' else 134
    c_dev_t = ctypes.c_uint
    c_fsblkcnt_t = c_win_ulong
    c_fsfilcnt_t = c_win_ulong
    c_gid_t = ctypes.c_uint
    c_mode_t = ctypes.c_uint
    c_off_t = ctypes.c_longlong
    c_pid_t = ctypes.c_int
    c_uid_t = ctypes.c_uint
    setxattr_t = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_byte), ctypes.c_size_t, ctypes.c_int)
    getxattr_t = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_byte), ctypes.c_size_t)
    c_stat._fields_ = [
        ('st_dev', c_dev_t),
        ('st_ino', ctypes.c_ulonglong),
        ('st_mode', c_mode_t),
        ('st_nlink', ctypes.c_ushort),
        ('st_uid', c_uid_t),
        ('st_gid', c_gid_t),
        ('st_rdev', c_dev_t),
        ('st_size', c_off_t),
        ('st_atimespec', c_timespec),
        ('st_mtimespec', c_timespec),
        ('st_ctimespec', c_timespec),
        ('st_blksize', ctypes.c_int),
        ('st_blocks', ctypes.c_longlong),
        ('st_birthtimespec', c_timespec)]
elif _system == 'OpenBSD':
    ENOTSUP = 91
    c_dev_t = ctypes.c_int32
    c_uid_t = ctypes.c_uint32
    c_gid_t = ctypes.c_uint32
    c_mode_t = ctypes.c_uint32
    c_off_t = ctypes.c_int64
    c_pid_t = ctypes.c_int32
    c_ino_t = ctypes.c_uint64
    c_nlink_t = ctypes.c_uint32
    c_blkcnt_t = ctypes.c_int64
    c_blksize_t = ctypes.c_int32
    setxattr_t = ctypes.CFUNCTYPE(
        ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_byte), ctypes.c_size_t, ctypes.c_int)
    getxattr_t = ctypes.CFUNCTYPE(
        ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_byte),
        ctypes.c_size_t)
    c_fsblkcnt_t = ctypes.c_uint64
    c_fsfilcnt_t = ctypes.c_uint64
    c_stat._fields_ = [
        ('st_mode', c_mode_t),
        ('st_dev', c_dev_t),
        ('st_ino', c_ino_t),
        ('st_nlink', c_nlink_t),
        ('st_uid', c_uid_t),
        ('st_gid', c_gid_t),
        ('st_rdev', c_dev_t),
        ('st_atimespec', c_timespec),
        ('st_mtimespec', c_timespec),
        ('st_ctimespec', c_timespec),
        ('st_size', c_off_t),
        ('st_blocks', c_blkcnt_t),
        ('st_blksize', c_blksize_t),
        ('st_flags', ctypes.c_uint32),
        ('st_gen', ctypes.c_uint32),
        ('st_birthtimespec', c_timespec),
    ]
else:
    raise NotImplementedError('%s is not supported.' % _system)


if _system == 'FreeBSD':
    c_fsblkcnt_t = ctypes.c_uint64
    c_fsfilcnt_t = ctypes.c_uint64
    setxattr_t = ctypes.CFUNCTYPE(
        ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_byte), ctypes.c_size_t, ctypes.c_int)

    getxattr_t = ctypes.CFUNCTYPE(
        ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_byte), ctypes.c_size_t)

    class c_statvfs(ctypes.Structure):
        _fields_ = [
            ('f_bavail', c_fsblkcnt_t),
            ('f_bfree', c_fsblkcnt_t),
            ('f_blocks', c_fsblkcnt_t),
            ('f_favail', c_fsfilcnt_t),
            ('f_ffree', c_fsfilcnt_t),
            ('f_files', c_fsfilcnt_t),
            ('f_bsize', ctypes.c_ulong),
            ('f_flag', ctypes.c_ulong),
            ('f_frsize', ctypes.c_ulong)]
elif _system == 'Windows' or _system == 'CYGWIN':
    class c_statvfs(ctypes.Structure):
        _fields_ = [
            ('f_bsize', c_win_ulong),
            ('f_frsize', c_win_ulong),
            ('f_blocks', c_fsblkcnt_t),
            ('f_bfree', c_fsblkcnt_t),
            ('f_bavail', c_fsblkcnt_t),
            ('f_files', c_fsfilcnt_t),
            ('f_ffree', c_fsfilcnt_t),
            ('f_favail', c_fsfilcnt_t),
            ('f_fsid', c_win_ulong),
            ('f_flag', c_win_ulong),
            ('f_namemax', c_win_ulong)]
else:
    class c_statvfs(ctypes.Structure):
        _fields_ = [
            ('f_bsize', ctypes.c_ulong),
            ('f_frsize', ctypes.c_ulong),
            ('f_blocks', c_fsblkcnt_t),
            ('f_bfree', c_fsblkcnt_t),
            ('f_bavail', c_fsblkcnt_t),
            ('f_files', c_fsfilcnt_t),
            ('f_ffree', c_fsfilcnt_t),
            ('f_favail', c_fsfilcnt_t),
            ('f_fsid', ctypes.c_ulong),
            # ('unused', ctypes.c_int),
            ('f_flag', ctypes.c_ulong),
            ('f_namemax', ctypes.c_ulong)]

if _system == 'Windows' or _system == 'CYGWIN':
    class fuse_file_info(ctypes.Structure):
        _fields_ = [
            ('flags', ctypes.c_int),
            ('fh_old', ctypes.c_int),
            ('writepage', ctypes.c_int),
            ('direct_io', ctypes.c_uint, 1),
            ('keep_cache', ctypes.c_uint, 1),
            ('flush', ctypes.c_uint, 1),
            ('padding', ctypes.c_uint, 29),
            ('fh', ctypes.c_uint64),
            ('lock_owner', ctypes.c_uint64)]
elif _system == "OpenBSD":
    class fuse_file_info(ctypes.Structure):
        _fields_ = [
            ('flags', ctypes.c_int32),
            ('fh_old', ctypes.c_uint32),
            ('writepage', ctypes.c_int32),
            ('direct_io', ctypes.c_uint32, 1),
            ('keep_cache', ctypes.c_uint32, 1),
            ('flush', ctypes.c_uint32, 1),
            ('nonseekable', ctypes.c_uint32, 1),
            ('padding', ctypes.c_uint32, 27),
            ('flock_release', ctypes.c_uint32, 1),
            ('fh', ctypes.c_uint64),
            ('lock_owner', ctypes.c_uint64)]
else:
    class fuse_file_info(ctypes.Structure):
        _fields_ = [
            ('flags', ctypes.c_int),
            ('fh_old', ctypes.c_ulong),
            ('writepage', ctypes.c_int),
            ('direct_io', ctypes.c_uint, 1),
            ('keep_cache', ctypes.c_uint, 1),
            ('flush', ctypes.c_uint, 1),
            ('nonseekable', ctypes.c_uint, 1),
            ('flock_release', ctypes.c_uint, 1),
            ('padding', ctypes.c_uint, 27),
            ('fh', ctypes.c_uint64),
            ('lock_owner', ctypes.c_uint64)]

if _system == "OpenBSD":
    class fuse_context(ctypes.Structure):
        _fields_ = [
            ('fuse', ctypes.c_voidp),
            ('uid', c_uid_t),
            ('gid', c_gid_t),
            ('pid', c_pid_t),
            ('private_data', ctypes.c_voidp),
            ('umask', c_mode_t),
        ]
else:
    class fuse_context(ctypes.Structure):
        _fields_ = [
            ('fuse', ctypes.c_voidp),
            ('uid', c_uid_t),
            ('gid', c_gid_t),
            ('pid', c_pid_t),
            ('private_data', ctypes.c_voidp)]

if _system == "OpenBSD":
    bmap_ret_t = ctypes.c_uint64
    extra_fields = []
else:
    bmap_ret_t = ctypes.c_ulonglong
    extra_fields = [
        ('flag_nullpath_ok', ctypes.c_uint, 1),
        ('flag_nopath', ctypes.c_uint, 1),
        ('flag_utime_omit_ok', ctypes.c_uint, 1),
        ('flag_reserved', ctypes.c_uint, 29),
        ('ioctl', ctypes.CFUNCTYPE(
            ctypes.c_int, ctypes.c_char_p, ctypes.c_uint, ctypes.c_void_p,
            ctypes.POINTER(fuse_file_info), ctypes.c_uint, ctypes.c_void_p)),
    ]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DEBUG
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':
    dump_globals(globals())
