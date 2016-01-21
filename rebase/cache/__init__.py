from multiprocessing import Queue, Process

from rebase.cache.main import cache_main

class CacheProcess(Process):
    def __init__(self, user_role_id):
        self.cache_id = user_role_id
        self.q = Queue()
        self.name = 'CacheProcess[{},{}]'.format(*user_role_id)
        super().__init__(
            name=self.name,
            target=cache_main,
            args=(user_role_id, self.q, self.name)
        )
        self.start()
