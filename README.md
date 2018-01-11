# pidlock

Simple PID based locking for cronjobs, UNIX scripts or python programs


### Requirement:

* requires python (>2 or 3)


### Usage:

* Install with pip

```bash
sudo pip install pidlock
```

* Use it from inside python script

```python
import time
from pidlock import PIDLock

locker = PIDLock()
with locker.lock(__file__, os.getpid()):
    time.sleep(5)
```

* Use it as commandline/cron job

```bash
pidlock 'sleep 2; sleep 2; sleep 2'
```


### Customization

You can pass PID file location and verbosity as arguments

```
locker = PIDLock(lockdir='~/anotherlockdir', verbose=False)
```
