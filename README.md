# FakeFS - *beta*


## Brief

Mirror existing directory with changes described in configuration file (using FUSE).


## Usage

`fakefs.py <mountpoint> <root> <configfile>`

The configuration file contains lines with one of the commands of `rm`, `mv` or `ln`:
* `rm <path>`: the specified file will be not accessible on the filsystem
* `mv <source-path> <target-path>`: the file will be moved to a new path
* `ln <source-path> <target-path>`: the file will e accessible on the target path as well

Example:
```
rm /swapfile
mv /opt/myapp/bin/myapp /usr/bin/myapp
ln /usr/bin/ls /usr/bin/ll
```

Preferred usage: fake the system root dierctory (`/`), then `chroot` to mount point.

Stop mirroring: `fusermount -u <mountpoint>`


## Known issues

- Works only for files, not directories
- Should be rewritten in C/C++


## Author

Forked from passthrough example:
https://github.com/skorokithakis/python-fuse-sample

Thanks for *skorokithakis*!
