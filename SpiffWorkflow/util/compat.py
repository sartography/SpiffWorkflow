try:
    from mutex import mutex

except ImportError:
    from threading import Lock

    class mutex(object):
        def __init__(self):
            self.lock = Lock()

        def lock(self):
            raise NotImplementedError

        def test(self):
            has = self.lock.acquire(blocking=False)
            if has:
                self.lock.release()

            return has

        def testandset(self):
            return self.lock.acquire(blocking=False)

        def unlock(self):
            self.lock.release()
