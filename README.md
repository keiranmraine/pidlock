[![PyPI version](https://img.shields.io/pypi/v/ansible.svg)](https://pypi.python.org/pypi/ansible)
[![Build Status](https://travis-ci.org/sayanarijit/pidlock.svg?branch=v1.0.4)](https://travis-ci.org/sayanarijit/pidlock)


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
pidlock -n sleepy_script -c 'sleep 10'
```


### Customization:

* You can pass PID file location and verbosity as arguments

```python
locker = PIDLock(lockdir='~/.pidlock', verbose=True)
```
