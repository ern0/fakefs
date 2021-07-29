#!/usr/bin/env python3

from __future__ import with_statement

import os
import sys
import errno
import shlex

from fuse import FUSE, FuseOSError, Operations


class Passthrough(Operations):

    def __init__(self, root, config):
        self.root = root
        self.procConfig(config)
    

    def fatal(self, message):
        sig = os.path.basename(sys.argv[0])
        print(f"{sig}: {message} at line {self.lineNo}", file=sys.stderr)
        quit()


    def procConfig(self, config):

        self.lineNo = 0
        self.sourceConfig = {}
        self.targetConfig = {}
        self.dirConfig = {}

        with open(config, "rt") as file:
            for line in file:      

                self.lineNo += 1

                line = line.strip()
                if line[0] == '#': continue
                items = shlex.split(line)

                try: action = items[0]
                except IndexError: continue
                if action not in ("rm", "mv", "ln"):
                    self.fatal(f"invalid action \"{action}\"")                

                try: source = items[1]
                except IndexError: self.fatal("missing source")

                try: target = items[2]
                except IndexError: target = None
                if action != "rm" and target is None:
                    self.fatal("missing target")
                
                self.sourceConfig[source] = (action, target,)
                if target is not None: self.targetConfig[target] = (action, source,)

            print(self.dirConfig)


    # Helpers
    # =======

    def _full_path(self, partial):
        partial = partial.lstrip("/")
        path = os.path.join(self.root, partial)
        
        return path
    

    def fake(self, path):

        print(path)

        if path in self.sourceConfig:
            (command, target) = self.sourceConfig[path]
            if command == "rm": return None
            elif command == "mv": return None
            elif command == "ln": pass

        if path in self.targetConfig:
            (command, source) = self.sourceConfig[path]
            if command == "rm": self.fatal("internal error")
            if command == "mv": return source
            if command == "ln": return source

        return path


    # Filesystem methods
    # ==================


    def access(self, path, mode):
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)


    def chmod(self, path, mode):
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)


    def chown(self, path, uid, gid):
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)


    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                     'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))


    def readdir(self, path, fh):
        full_path = self._full_path(path)

        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))

        # TODO: append files which copied or moved to this directory
        print("directory: " + path)
        print(dirents)

        for entry in dirents:            

            fullEntry = (path + entry)
            fullEntry = self.fake(fullEntry)
            if fullEntry is None: continue

            entry = os.path.basename(fullEntry)
            yield entry


    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname


    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)


    def rmdir(self, path):
        full_path = self._full_path(path)
        return os.rmdir(full_path)


    def mkdir(self, path, mode):
        return os.mkdir(self._full_path(path), mode)


    def statfs(self, path):
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))


    def unlink(self, path):
        return os.unlink(self._full_path(path))


    def symlink(self, name, target):
        return os.symlink(name, self._full_path(target))


    def rename(self, old, new):
        return os.rename(self._full_path(old), self._full_path(new))


    def link(self, target, name):
        return os.link(self._full_path(target), self._full_path(name))


    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)


    # File methods
    # ============

    def open(self, path, flags):

        path = self.fake(path)
        if path is None: return os.open("/_not_found", flags)

        full_path = self._full_path(path)
        return os.open(full_path, flags)


    def create(self, path, mode, fi=None):
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)


    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)


    def write(self, path, buf, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)


    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)


    def flush(self, path, fh):
        return os.fsync(fh)


    def release(self, path, fh):
        return os.close(fh)


    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)


def main(mountpoint, root, config):
    FUSE(Passthrough(root, config), mountpoint, nothreads=True, foreground=True)


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        main(sys.argv[2], sys.argv[1], sys.argv[3])
    else:
        print(f"usage: {os.path.basename(sys.argv[0])} <mountpoint> <root> <config>")
