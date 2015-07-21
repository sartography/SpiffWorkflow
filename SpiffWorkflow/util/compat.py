try:
    # python 2
    from mutex import mutex
    import ConfigParser as configparser

except ImportError:
    # python 3
    import configparser
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
