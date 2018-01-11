# -*-coding: utf-8 -*-
'''
Author:         Arijit Basu
Email:          sayanarijit@gmail.com
Documentation:  https://github.com/sayanarijit/pidlock
'''

from __future__ import print_function
import re
import os
import sys
from contextlib import contextmanager


VERSION = 'v1.0.0'

class PIDLockedException(Exception):
    def __init__(self, name, pid):
        Exception.__init__(self, '"{}" is already locked with PID: {}'.format(name, pid))


class PIDLock:
    """
    PARAMETERS:
        lockdir: str: (default: ~/.pidlock) Where to create/store PID lock files
        verbose: bool: (default: True) Verbosity
    RAISES:
        PIDLockedException
    EXAMPLE:
        locker = PIDLock()
        with locker.lock('sleepy_script', os.getpid()):
            time.sleep(5)
    """
    def __init__(self, lockdir='~/.pidlock', verbose=True):
        self.lockdir = os.path.expanduser(lockdir)
        self.verbose = verbose

    @contextmanager
    def lock(self, name, pid):
        if not os.path.isdir(self.lockdir): os.mkdir(self.lockdir)

        pidfile = os.path.join(self.lockdir, name + ".pid")

        # If lock exists
        if os.path.isfile(pidfile):
            f = open(pidfile)
            xpid = int(f.read())
            f.close()
            # If pid exists, quit
            pids = [int(x.split()[1]) for x in os.popen("ps -eaf").read().splitlines()[1:]]
            if xpid in pids:
                raise PIDLockedException(name, xpid)
            # Else remove lock
            os.remove(pidfile)

        # Else create lock
        if self.verbose:
            print('Locking "{}" with PID: {}'.format(name, pid))
        f = open(pidfile, "w")
        f.write(str(pid))
        f.close()

        try:
            # Perform the task
            yield
        finally:
            # Finally close the PID file
            if self.verbose:
                print('Released lock...')
            os.remove(pidfile)


def cli_lock():
    """
    CLI interface for PID based locking
    EXAMPLE:
        pidlock 'sleep 2; sleep 2; sleep 2'
    """
    commands = sys.argv[1:]
    if len(commands) == 0:
        return
    name = re.sub('[^0-9a-zA-Z]', '', ''.join(sys.argv[1:]))

    locker = PIDLock()
    with locker.lock(name, os.getpid()):
        print("Running command:"," ".join(commands))
        os.system(" ".join(commands))


if __name__ == "__main__":
    cli_lock()
