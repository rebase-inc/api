from time import process_time

class StopWatch(object):
    def __init__(self):
        self.elapsed = None
        self.start = None

    def __enter__(self):
        self.start = process_time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end = process_time()
        self.elapsed = end - self.start
        return False

class PrintElapsedTime(StopWatch):
    def __exit__(self, exc_type, exc_val, exc_tb):
        print('Elapsed: {} seconds'.format(process_time() - self.start))
        return False

class Elapsed(StopWatch):
    def __init__(self, on_elapsed=None):
        self.on_elapsed = on_elapsed
        super().__init__(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        ret = super().__exit__(self, exc_type, exc_val, exc_tb)
        self.on_elapsed(self.elapsed)
        return ret
