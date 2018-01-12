[![PyPI version](https://img.shields.io/pypi/v/pidlock.svg)](https://pypi.python.org/pypi/pidlock)
[![Build Status](https://travis-ci.org/sayanarijit/pidlock.svg?branch=master)](https://travis-ci.org/sayanarijit/pidlock)


# pidlock

Simple PID based locking for cronjobs, UNIX scripts or python programs


### Requirement:

* requires python (>2 or 3)


### Usage:

* Install with pip

```bash
sudo pip install -U pidlock
```

* Use it from inside python script

```python
import time
from pidlock import PIDLock

locker = PIDLock()
with locker.lock('sleepy_script'):
    time.sleep(10)
```

* Use it as commandline/cron job

```bash
# To display help menu
pidlock -h    # Or pidlock --help

# Example usage
pidlock -n sleepy_script -c 'sleep 10'

# Same as
pidlock --name sleepy_script --command 'sleep 10'
```


### Customization:

* You can pass PID file location and verbosity as arguments

```python
# Python Usage
locker = PIDLock(lockdir='~/.pidlock', verbose=True)
```
```bash
# Commandline usage
pidlock -n sleepy_script -c 'sleep 10' -l ~/.pidlock -v

# Same as
pidlock --name sleepy_script --command 'sleep 10' --lockdir ~/.pidlock --verbose
```
