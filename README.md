# pidlock

[![PyPI version](https://img.shields.io/pypi/v/pidlock.svg)](https://pypi.python.org/pypi/pidlock)
[![CircleCI](https://circleci.com/gh/keiranmraine/pidlock/tree/develop.svg?style=svg))](https://circleci.com/gh/keiranmraine/pidlock/tree/develop)

Simple PID based locking for cronjobs, UNIX scripts or python programs.  Copes with locking between hosts.

## Requirement

- requires python3

## Usage

- Install with pip

```
sudo pip install -U pidlock
```

- Use it from inside python script

```
import time
from pidlock import PIDLock

locker = PIDLock()
with locker.lock('sleepy_script'):
    time.sleep(10)
```

- Use it as commandline/cron job

```
# To display help menu
pidlock -h    # Or pidlock --help

# Example usage
pidlock -n sleepy_script -c 'sleep 10'

# Same as
pidlock --name sleepy_script --command 'sleep 10'
```

### Customization:

- You can pass PID file location, verbosity, time limit and minimum interval as arguments

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

## Contributions

Originally written and published by [Arijit Basu](https://github.com/sayanarijit/).  Adaptation to cope with race conditions
by Keiran Raine (ongoing owner/support).
