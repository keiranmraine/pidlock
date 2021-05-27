from pidlock import PIDLock, PIDLockedException
import pytest
from multiprocessing import Process
import time

locker = PIDLock("tests")


def run_in_separate_process(func, args):
    p = Process(target=func, args=args)
    p.start()
    return p


def lock_and_sleep(secs, wait=0, mininterval=1):
    with locker.lock("test_and_sleep", wait=wait, mininterval=mininterval):
        time.sleep(secs)


def test_lock():
    start = time.time()
    lock_and_sleep(1)
    end = time.time()

    assert int(end - start) == 1


def test_already_locked():
    t = run_in_separate_process(lock_and_sleep, (3,))

    time.sleep(1)
    with pytest.raises(PIDLockedException):
        lock_and_sleep(1)

    t.join()
