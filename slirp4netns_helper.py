#!/usr/bin/env python
import ctypes
import ctypes.util
import fcntl
import os
import sys

SYSCALL_SETNS: int = 308
NS_GET_PARENT: int = 46850

libc = ctypes.CDLL(ctypes.util.find_library("c"))
setns = libc.syscall
setns.argtypes = [ctypes.c_long, ctypes.c_int, ctypes.c_int]

pid = sys.argv[1]

userns_fd = os.open(f"/proc/{pid}/ns/user", os.O_RDONLY | os.O_CLOEXEC)
parent_userns_fd = fcntl.ioctl(userns_fd, NS_GET_PARENT)

setns(SYSCALL_SETNS, parent_userns_fd, 0)

os.execv(
    "/usr/bin/slirp4netns",
    [
        "/usr/bin/slirp4netns",
        "--configure",
        "--enable-sandbox",
        "--userns=/proc/self/ns/user",
    ],
)
