from multiprocessing import Queue, Process

from rebase.cache.main import cache_main


class CacheProcess(Process):
    def __init__(self,role_id):
        self.q = Queue()
        self.name = 'CacheChild({})'.format(role_id)
        super().__init__(
            name=self.name,
            target=cache_main,
            args=(role_id, self.q, self.name)
        )
        self.start()
