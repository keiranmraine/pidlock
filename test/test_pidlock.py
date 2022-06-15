

#!/usr/bin/env python
# -*-coding: utf-8 -*-
"""
Original Author:         Arijit Basu
Supporting Author:       Keiran Raine <keiranmraine@gmail.com>
Documentation:  https://github.com/keiranmraine/pidlock#pidlock
"""

# from __future__ import print_function
import os
import shutil
import time
from unittest import TestCase
from unittest.mock import patch
from os.path import exists

from os import path
from codecs import open
import pkg_resources  # part of setuptools
import pathlib

from pidlock import PIDLock, PIDCorruptException, PIDLockedException

THISPATH = pathlib.Path(__file__).parent.resolve()


VERSION = pkg_resources.require("pidlock")[0].version

class TestPidlock(TestCase):
    def test_init(self):
        testee = PIDLock("/etc/pidlock")
        self.assertEqual("/etc/pidlock", testee.lockdir)
        self.assertTrue(testee.verbose)

        home = path.expanduser("~")

        testee = PIDLock('~/.pidlock', verbose=False)
        self.assertEqual(f'{home}/.pidlock', testee.lockdir)
        self.assertFalse(testee.verbose)

    @patch('pidlock.getfqdn')
    def test_lock(self, mock_getfqdn):
        mock_getfqdn.return_value = 'my.host.com'
        testee = PIDLock(f'{THISPATH}/props')
        this_pid = os.getpid()
        lockdir = f'{THISPATH}/props/testlock'
        lockfilepath = f'{THISPATH}/props/testlock/lock.pid'
        shutil.rmtree(lockdir, ignore_errors=True)
        with testee.lock('testlock'):
            self.assertTrue(exists(lockfilepath))
            with open(lockfilepath, 'r') as lockfile:
                content = lockfile.read()
                self.assertEqual(f'{this_pid}\tmy.host.com\n', content)
        self.assertFalse(exists(lockfilepath))

        os.makedirs(lockfilepath)
        try:
            with testee.lock('testlock'):
                 raise ValueError("This should raise PIDCorruptException")
        except PIDCorruptException:
            pass
        os.rmdir(lockfilepath)
        with open(lockfilepath, 'w') as lockfile:
            lockfile.write('this should crash it')
        try:
            with testee.lock('testlock'):
                 raise ValueError("This should raise ValueError")
            raise ValueError("This should raise ValueError")
#            self.assertRaises(ValueError, testee.lock, 'testlock')
        except ValueError:
            pass
        with open(lockfilepath, 'w') as lockfile:
            print(f'{this_pid}\tmy.host.com', file=lockfile)
        try:
            with testee.lock('testlock'):
                raise ValueError("This should raise PIDLockedException")
            raise ValueError("This should raise PIDLockedException")
        #            self.assertRaises(ValueError, testee.lock, 'testlock')
        except PIDLockedException:
            pass
        shutil.rmtree(lockdir, ignore_errors=True)



