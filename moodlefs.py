from errno import ENOENT, EACCES

import fuse
from fuse import LoggingMixIn, Operations, FuseOSError

from FSNode import FSNode

# a simple read-only filesystem to-tree interface
class MoodleFS(LoggingMixIn, Operations):
    'Example memory filesystem. Supports only one level of files.'

    def __init__(self, moodle):
        self.category_name_id_map = {}
        self.moodle = moodle
        self.tree = FSNode.from_moodle(self.moodle)

    def chmod(self, path, mode):
        raise fuse.FuseOSError(EACCES)

    def chown(self, path, uid, gid):
        raise fuse.FuseOSError(EACCES)

    def create(self, path, mode):
        raise fuse.FuseOSError(EACCES)

    def getattr(self, path, fh=None):
        s = self.tree.resolve_path(path)
        if s is None:
            raise FuseOSError(ENOENT)
        return s.to_stat_struct()

    def getxattr(self, path, name, position=0):
        pass

    def listxattr(self, path):
        return []

    def mkdir(self, path, mode):
        raise fuse.FuseOSError(EACCES)

    def open(self, path, flags):
        return 120

    def read(self, path, size, offset, fh):
        return self.tree.resolve_path(path).read(size, offset, self.moodle)

    def readdir(self, path, fh):
        dir_e = self.tree.resolve_path(path)
        return ['.', '..'] + [child.name for child in dir_e.children]

    def readlink(self, path):
        pass

    def removexattr(self, path, name):
        pass

    def rename(self, old, new):
        raise fuse.FuseOSError(EACCES)

    def rmdir(self, path):
        raise fuse.FuseOSError(EACCES)

    def setxattr(self, path, name, value, options, position=0):
        pass

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
        raise fuse.FuseOSError(EACCES)

    def truncate(self, path, length, fh=None):
        raise fuse.FuseOSError(EACCES)

    def unlink(self, path):
        raise fuse.FuseOSError(EACCES)

    def utimens(self, path, times=None):
        pass

    def write(self, path, data, offset, fh):
        raise fuse.FuseOSError(EACCES)
