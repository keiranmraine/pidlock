#!/usr/bin/env python
# -*-coding: utf-8 -*-
"""
Original Author:         Arijit Basu
Supporting Author:       Keiran Raine <keiranmraine@gmail.com>
Documentation:  https://github.com/keiranmraine/pidlock#pidlock
"""

from __future__ import print_function
import os
import sys
import time
import psutil
import shutil
from os import path
from codecs import open
from subprocess import Popen
from contextlib import contextmanager
from socket import getfqdn
import pkg_resources  # part of setuptools


VERSION = pkg_resources.require("pidlock")[0].version


class PIDLockedException(Exception):
    def __init__(self, name, pid, host):
        Exception.__init__(
            self,
            "'{}' is already locked with PID: {} on host: {}".format(name, pid, host),
        )


class PIDCorruptException(Exception):
    def __init__(self, name):
        Exception.__init__(
            self, "Lock directory exists witout a lock.pid file: {}".format(name)
        )


class PIDLock:
    """PIDLock class

    Args:
        lockdir: (str) Where to create/store PID locks. Default is '~/.pidlock'
        verbose: (bool) Prints verbose outputs. Default is False
    Example:
        >>> from pidlock import PIDLock
        >>> locker = PIDLock(lockdir='~/.pidlock', verbose=True)
    """

    def __init__(self, lockdir="~/.pidlock", verbose=True):
        self.lockdir = path.expanduser(lockdir)
        self.verbose = verbose

    @contextmanager
    def lock(self, name, wait=0, mininterval=1):
        """Locks process till codes inside "with" block is executed

        Args:
            name: (str) Name of the directory to be used as lock
            wait: (float) How long (sec.) should it wait for lock to be released. Default is 0
            mininterval: (float) Minimum interval (sec.) to balance between performance and resource usage. Default is 1
        Raises:
            PIDLockedException: PID file is locked by another process
        Example:
            >>> with locker.lock(name='sleepy_script', wait=0, mininterval=1):
            >>>     time.sleep(10)
        """
        # create the top level directory, race isn't an issue on this
        if not path.isdir(self.lockdir):
            os.makedirs(self.lockdir, exist_ok=True)

        piddir = path.join(self.lockdir, name)
        pidfile = path.join(piddir, "lock.pid")
        this_pid = os.getpid()
        this_host = getfqdn()

        max_time = time.time() + wait
        first = True

        while True:
            if first:
                first = False
            else:
                time.sleep(mininterval)
            try:
                os.mkdir(piddir)
                with open(pidfile, "wt") as p_fh:
                    print(f"{this_pid}\t{this_host}", file=p_fh)
                    p_fh.flush()
                    os.fsync(p_fh)
                # we created the directory so we win the lock
                break
            except FileExistsError as fe:
                if path.exists(piddir):
                    if not path.isfile(pidfile):
                        # wait a little then check the dir still exists
                        time.sleep(1)
                        if path.exists(piddir) and not path.isfile(pidfile):
                            raise PIDCorruptException(piddir)
                        # reset this as a new lock may be created before we get to it
                        continue

                    ## dir and pid file exist
                    with open(pidfile, "rt") as p_fh:
                        (lock_pid, lock_host) = p_fh.readline().strip().split("\t")
                    if lock_host == this_host:
                        lock_pid = int(lock_pid)
                        # now we can look for the pid to see if we should clean it
                        pids = psutil.pids()
                        if lock_pid not in pids:
                            # no pid, safe to clean, just incase several processes try, don't error
                            if self.verbose:
                                print("Removing old piddir...")
                            shutil.rmtree(piddir, ignore_errors=True)
                            continue

                    if self.verbose:
                        print(
                            f"Locked with PID: {lock_pid} on host: {lock_host}, {pidfile}."
                        )
                        print("Waiting for lock to be released...")
                    if time.time() > max_time:
                        raise PIDLockedException(name, lock_pid, lock_host)
            # Wait till it's released or time limit is over
            # all of above logic needs to run between iterations

        try:
            # Perform the task
            yield
        finally:
            # Finally remove the PID dir
            shutil.rmtree(piddir, ignore_errors=True)
            if self.verbose:
                print("Released lock...")


def pidlock_cli():
    """CLI interface for PID based locking

    Usage:
        pidlock [-h] -n NAME -c COMMAND [--version]
    Returns:
        Returns the returncode returned by the executed command
    Example:
        $ pidlock -n sleepy_script -c 'sleep 10'
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="pidlock",
        description="Simple PID based locking for cronjobs, UNIX scripts or python programs",
    )
    parser.add_argument("-n", "--name", help="name of the lock file", required=True)
    parser.add_argument(
        "-c", "--command", help="commands/script to be executed", required=True
    )
    parser.add_argument(
        "-l",
        "--lockdir",
        help="directory to keep lock files. (default: ~/.pidlock)",
        default="~/.pidlock",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="use this flag to make it verbose. (default: False)",
        default=False,
    )
    parser.add_argument(
        "-w",
        "--wait",
        type=float,
        help="how long (sec.) to wait for PID file to be released. (default: 0)",
        default=0,
    )
    parser.add_argument(
        "-m",
        "--mininterval",
        type=float,
        help="minimum interval (sec.) to balance between performance and resource usage. (default: 1)",
        default=1,
    )
    parser.add_argument(
        "-V", "--version", action="version", version="pidlock " + VERSION
    )

    parsed = parser.parse_args()

    locker = PIDLock(lockdir=parsed.lockdir, verbose=parsed.verbose)
    try:
        with locker.lock(
            name=parsed.name, wait=parsed.wait, mininterval=parsed.mininterval
        ):
            if parsed.verbose:
                print("Running command:", parsed.command)
            quit(Popen(parsed.command, shell=True).wait())
    except PIDLockedException as e:
        print("pidlock:", e, file=sys.stderr)
        quit(1)
    except Exception as e:
        print("pidlock:", e, file=sys.stderr)
        quit(3)


if __name__ == "__main__":
    pidlock_cli()
