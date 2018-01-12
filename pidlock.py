# -*-coding: utf-8 -*-
'''
Author:         Arijit Basu
Email:          sayanarijit@gmail.com
Documentation:  https://github.com/sayanarijit/pidlock
'''

from __future__ import print_function
import os
import sys
import psutil
from os import path
from codecs import open
from contextlib import contextmanager


VERSION = 'v1.1.0'


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
        self.lockdir = path.expanduser(lockdir)
        self.verbose = verbose

    @contextmanager
    def lock(self, name):
        if not path.isdir(self.lockdir): os.mkdir(self.lockdir)

        pidfile = path.join(self.lockdir, name + ".pid")
        pid = os.getpid()

        # If lock exists
        if path.isfile(pidfile):
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
    parser.add_argument('-n', '--name',
        help='name of the lock file', required=True)
    parser.add_argument('-c', '--command',
        help='commands/script to be executed', required=True)
    parser.add_argument('-l', '--lockdir',
        help='directory to keep lock files. (default: ~/.pidlock)', default='~/.pidlock')
    parser.add_argument('-v', '--verbose',
        action='store_true', help='use this flag to make it verbose. (default: False)', default=False)
    parser.add_argument('-V', '--version',
        action='version', version='pidlock '+VERSION)

    parsed = parser.parse_args()

    locker = PIDLock(parsed.lockdir, parsed.verbose)
    try:
        with locker.lock(parsed.name):
            if parsed.verbose:
                print("Running command:", parsed.command)
            quit(os.system(parsed.command))
    except PIDLockedException as e:
        print('pidlock:', e, file=sys.stderr)
        quit(1)
    except Exception as e:
        print('pidlock:', e, file=sys.stderr)
        quit(3)


if __name__ == "__main__":
    pidlock_cli()
