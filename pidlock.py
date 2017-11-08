#!/bin/env python

from __future__ import print_function
import os
import sys
from contextlib import contextmanager
from subprocess import Popen


LOCKDIR = "/var/run/pidlock"


@contextmanager
def lock(name, pid):
    if not os.path.isdir(LOCKDIR): os.mkdir(LOCKDIR)

    pidfile = os.path.join(LOCKDIR, name + ".pid")

    # If lock exists
    if os.path.isfile(pidfile):
        f = open(pidfile)
        xpid = int(f.read())
        f.close()
        # If pid exists, quit
        pids = [int(x.split()[1]) for x in os.popen("ps -eaf").read().splitlines()[1:]]
        if xpid in pids:
            print(name+": Lock is already aquired by pid:", xpid)
            quit()
        # Else remove lock
        os.remove(pidfile)

    # Else create lock
    print("Locking",name,"with PID:",pid)
    f = open(pidfile, "w")
    f.write(str(pid))
    f.close()

    try:
        # Perform the task
        yield
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    finally:
        # Finally close the PID file
        print("Releasing lock")
        os.remove(pidfile)


if __name__ == "__main__":

    commands = sys.argv[1:]
    name = commands[0].split(";")[0].split("/")[-1]

    with lock(name, os.getpid()):
        print("Running command:"," ".join(commands))
        os.system(" ".join(commands))
