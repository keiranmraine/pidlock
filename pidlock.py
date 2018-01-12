# -*-coding: utf-8 -*-
'''
Author:         Arijit Basu
Email:          sayanarijit@gmail.com
Documentation:  https://github.com/sayanarijit/pidlock
'''

from __future__ import print_function
import os
import psutil
from codecs import open
from contextlib import contextmanager


with open('VERSION', encoding='utf-8') as f:
    VERSION = f.read()


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
        import time
        from pidlock import PIDLock
        locker = PIDLock()
        with locker.lock('sleepy_script'):
            time.sleep(10)
    """
    def __init__(self, lockdir='~/.pidlock', verbose=True):
        self.lockdir = os.path.expanduser(lockdir)
        self.verbose = verbose

    @contextmanager
    def lock(self, name):
        if not os.path.isdir(self.lockdir): os.mkdir(self.lockdir)

        pidfile = os.path.join(self.lockdir, name + ".pid")
        pid = os.getpid()

        # If lock exists
        if os.path.isfile(pidfile):
            f = open(pidfile, encoding='utf-8')
            xpid = int(f.read())
            f.close()
            # If pid exists, quit
            pids = psutil.pids()
            pids.remove(pid)
            if xpid in pids:
                raise PIDLockedException(name, xpid)
            # Else remove lock
            os.remove(pidfile)

        # Else create lock
        if self.verbose:
            print('Locking "{}" with PID: {}'.format(name, pid))
        f = open(pidfile, "w", encoding='utf-8')
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


def pidlock_cli():
    """
    CLI interface for PID based locking
    USAGE:
        pidlock [-h] -n NAME -c COMMAND [--version]
    EXAMPLE:
        pidlock -n sleepy_script -c 'sleep 10'
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog='pidlock',
        description='Simple PID based locking for cronjobs, UNIX scripts or python programs'
    )
    parser.add_argument('-n', dest='name', help='name of the lock file', required=True)
    parser.add_argument('-c', dest='command', help='commands/script to be executed', required=True)
    parser.add_argument('--version', action='version', version='pidlock '+VERSION)

    parsed = parser.parse_args()

    locker = PIDLock()
    with locker.lock(parsed.name):
        print("Running command:", parsed.command)
        os.system(parsed.command)


if __name__ == "__main__":
    pidlock_cli()
