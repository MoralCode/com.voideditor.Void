#!/usr/bin/env python

import argparse
import ctypes
import ctypes.util
import fcntl
import logging
import os
import sys
from typing import NoReturn

# --- Constants ---
# It's better practice to get the syscall number from the OS headers
# if possible, but for a simple script, defining them is okay.
# Note: These numbers can vary between architectures (e.g., x86_64 vs aarch64).
SYSCALL_SETNS: int = 308  # Syscall number for setns on x86_64
NS_GET_PARENT: int = 46850  # IOCTL code for NS_GET_PARENT

# --- Logging Setup ---
# Set up a simple logger that prints to stderr.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# --- Type-hinted Syscall Setup ---
try:
    # Find the standard C library
    libc_path: str | None = ctypes.util.find_library("c")
    if libc_path is None:
        raise OSError("Standard C library not found.")

    libc: ctypes.CDLL = ctypes.CDLL(libc_path, use_errno=True)

    # Define the syscall function signature for setns
    syscall = libc.syscall
    syscall.argtypes = [ctypes.c_long, ctypes.c_int, ctypes.c_int]
    syscall.restype = ctypes.c_int

except (AttributeError, OSError) as e:
    logging.error(f"Failed to set up syscall interface: {e}")
    sys.exit(1)


def die(message: str) -> NoReturn:
    """Prints an error message to stderr and exits the program."""
    logging.error(message)
    sys.exit(1)


def main() -> None:
    """
    Main function to parse arguments and perform the namespace switch.
    """
    parser = argparse.ArgumentParser(
        description="Enter the parent user namespace of a process.",
        epilog="This script must be run with sufficient privileges (e.g., as root) "
        "to perform the setns syscall into an arbitrary namespace.",
    )
    parser.add_argument(
        "pid",
        type=int,
        help="The Process ID (PID) of a process in the child namespace.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose DEBUG logging."
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="The command to execute in the parent namespace. Defaults to the user's shell.",
    )

    args: argparse.Namespace = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose logging enabled.")

    pid: int = args.pid
    user_ns_path: str = f"/proc/{pid}/ns/user"
    logging.debug(f"Targeting user namespace file: {user_ns_path}")

    # 1. Get a file descriptor for the child's user namespace
    try:
        userns_fd: int = os.open(user_ns_path, os.O_RDONLY | os.O_CLOEXEC)
        logging.debug(f"Successfully opened {user_ns_path}, got fd={userns_fd}")
    except FileNotFoundError:
        die(f"PID {pid} or its namespace file does not exist. Is the process running?")
    except PermissionError:
        die(f"Permission denied to open {user_ns_path}. Try running with sudo.")
    except Exception as e:
        die(f"An unexpected error occurred while opening the namespace file: {e}")

    # 2. Use ioctl to get the parent namespace's file descriptor
    try:
        parent_userns_fd: int = fcntl.ioctl(userns_fd, NS_GET_PARENT)
        logging.debug(
            f"Successfully got parent namespace fd={parent_userns_fd} via ioctl."
        )
    except OSError as e:
        die(
            f"ioctl(NS_GET_PARENT) failed: {e}. Are you sure this is a child namespace?"
        )
    finally:
        os.close(userns_fd)
        logging.debug(f"Closed child namespace fd={userns_fd}")

    # 3. Call setns to switch to the parent namespace
    logging.info(f"Attempting to switch to parent namespace (fd={parent_userns_fd})...")
    if syscall(SYSCALL_SETNS, parent_userns_fd, 0) == -1:
        errno: int = ctypes.get_errno()
        os.close(parent_userns_fd)
        die(f"setns syscall failed: {os.strerror(errno)} (errno={errno})")

    logging.info("Successfully switched to parent user namespace.")
    os.close(parent_userns_fd)
    logging.debug(f"Closed parent namespace fd={parent_userns_fd}")

    # 4. Execute the desired command
    if not args.command:
        cmd_to_run: list[str] = [
            "/usr/bin/slirp4netns",
            "--configure",
            "--enable-sandbox",
            "--userns=/proc/self/ns/user",
            "--disable-host-loopback",
            f"{pid}",
            "tap0",
        ]
    else:
        cmd_to_run: list[str] = args.command
    logging.info(f"Executing command: {' '.join(cmd_to_run)}")

    try:
        os.execvp(cmd_to_run[0], cmd_to_run)
    except FileNotFoundError:
        die(f"Command not found: {cmd_to_run[0]}")
    except Exception as e:
        die(f"Failed to execute command: {e}")


if __name__ == "__main__":
    main()  #!/usr/bin/env python
