[![PyPI version](https://img.shields.io/pypi/v/pidlock.svg)](https://pypi.python.org/pypi/pidlock)
[![Build Status](https://travis-ci.org/sayanarijit/pidlock.svg?branch=master)](https://travis-ci.org/sayanarijit/pidlock)


# pidlock

Simple PID based locking for cronjobs, UNIX scripts or python programs


### Requirement:

* requires python (>2 or 3)


### Usage:

* Install with pip

```
sudo pip install -U pidlock
```

* Use it from inside python script

```
import time
from pidlock import PIDLock

locker = PIDLock()
with locker.lock('sleepy_script'):
    time.sleep(10)
```

* Use it as commandline/cron job

```
# To display help menu
pidlock -h    # Or pidlock --help

# Example usage
pidlock -n sleepy_script -c 'sleep 10'

# Same as
pidlock --name sleepy_script --command 'sleep 10'
```


### Customization:

* You can pass PID file location, verbosity, time limit and minimum interval as arguments

```
# Python Usage
locker = PIDLock(lockdir='~/.pidlock', verbose=True)

with locker.lock('sleepy_script', wait=10, mininterval=1):
    time.sleep(10)
```
```
# Commandline usage
pidlock -n sleepy_script -c 'sleep 10' -l ~/.pidlock -v -w 10 -m 1

# Same as
pidlock --name sleepy_script --command 'sleep 10' --lockdir ~/.pidlock --verbose --wait 10 --mininterval 1
```
