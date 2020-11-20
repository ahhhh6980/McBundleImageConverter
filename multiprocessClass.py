import multiprocessing.pool

class NonDaemon(multiprocessing.Process):
    def _get_daemon(self): return False
    def _set_daemon(self, value): pass
    daemon = property(_get_daemon, _set_daemon)

class nPool(multiprocessing.pool.Pool): Process = NonDaemon
