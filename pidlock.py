# -*-coding: utf-8 -*-
'''
Author:         Arijit Basu <sayanarijit@gmail.com>
Documentation:  https://github.com/sayanarijit/pidlock#pidlock
'''

from __future__ import print_function
import os
import sys
import time
import psutil
from os import path
from codecs import open
from subprocess import Popen
from contextlib import contextmanager


VERSION = 'v2.0.0'


class PIDLockedException(Exception):
    def __init__(self, name, pid):
        Exception.__init__(self, '"{}" is already locked with PID: {}'.format(name, pid))


class PIDLock:
    """PIDLock class

    Args:
        lockdir: (str) Where to create/store PID lock files. Default is '~/.pidlock'
        verbose: (bool) Prints verbose outputs. Default is False
    Example:
        >>> from pidlock import PIDLock
        >>> locker = PIDLock(lockdir='~/.pidlock', verbose=True)
    """
    def __init__(self, lockdir='~/.pidlock', verbose=True):
        self.lockdir = path.expanduser(lockdir)
        self.verbose = verbose

    @contextmanager
    def lock(self, name, wait=0, mininterval=1):
        """Locks process till codes inside "with" block is executed

        Args:
            name: (str) Name of the file to be used as lock
            wait: (float) How long (sec.) should it wait for lock to be released. Default is 0
            mininterval: (float) Minimum interval (sec.) to balance between performance and resource usage. Default is 1
        Raises:
            PIDLockedException: PID file is locked by another process
        Example:
            >>> with locker.lock(name='sleepy_script', wait=0, mininterval=1):
            >>>     time.sleep(10)
        """
        if not path.isdir(self.lockdir): os.mkdir(self.lockdir)

        pidfile = path.join(self.lockdir, name + ".pid")
        pid = os.getpid()

        # If lock exists
        if path.isfile(pidfile):
            f = open(pidfile, encoding='utf-8')
            xpid = int(f.read())
            f.close()
            # If pid exists
            pids = psutil.pids()
            pids.remove(pid)
            if xpid in pids:
                if self.verbose:
                    print('PID file is locked with PID:', xpid)
                    print('Waiting for lock to be released...')

                # Wait till it's released or time limit is over
                now = time.time()
                while time.time() - now < wait and xpid in pids:
                    if self.verbose:
                        print('Still waiting...')
                    time.sleep(mininterval)
                    pids = psutil.pids()
                    pids.remove(pid)

                if xpid in pids:
                    # Time limit is over, raise exception
                    raise PIDLockedException(name, xpid)

            # Else remove lock
            else:
                if self.verbose:
                    print('Removing old pidfile...')
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
            os.remove(pidfile)
            if self.verbose:
                print('Released lock...')


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
    parser.add_argument('-w', '--wait',
        type=float, help='how long (sec.) to wait for PID file to be released. (default: 0)', default=0)
    parser.add_argument('-m', '--mininterval',
        type=float, help='minimum interval (sec.) to balance between performance and resource usage. (default: 1)', default=1)
    parser.add_argument('-V', '--version',
        action='version', version='pidlock '+VERSION)

    parsed = parser.parse_args()

    locker = PIDLock(lockdir=parsed.lockdir, verbose=parsed.verbose)
    try:
        with locker.lock(name=parsed.name, wait=parsed.wait, mininterval=parsed.mininterval):
            if parsed.verbose:
                print("Running command:", parsed.command)
            quit(Popen(parsed.command, shell=True).wait())
    except PIDLockedException as e:
        print('pidlock:', e, file=sys.stderr)
        quit(1)
    except Exception as e:
        print('pidlock:', e, file=sys.stderr)
        quit(3)


if __name__ == "__main__":
    pidlock_cli()
