from logging import getLogger
from time import perf_counter


logger = getLogger()


class StopWatch(object):
    def __init__(self, clock=perf_counter):
        self.elapsed = None
        self.start_time = None
        self.clock = clock

    def __enter__(self):
        self.start_time = self.clock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end = self.clock()
        self.elapsed = end - self.start_time
        return False


class WhenDone(StopWatch):

    def __enter__(self):
        super().__enter__()
        self.on_start()


    def __exit__(self, exc_type, exc_val, exc_tb):
        ret = super().__exit__(exc_type, exc_val, exc_tb)
        self.on_stop()
        return ret

    def on_start(self):
        pass

    def on_stop(self):
        pass


class PrintElapsedTime(WhenDone):

    start = 'Start'
    stop = 'Stop: {} seconds elapsed'

    def __init__(self, start=None, stop=None):
        self.stop = stop if stop else PrintElapsedTime.stop
        self.start = start if start else PrintElapsedTime.start
        super().__init__()

    def on_start(self):
        print(self.start)

    def on_stop(self):
        print(self.stop.format(self.elapsed))


class LogElapsedTime(WhenDone):

    start = 'Start:'
    stop = 'Stop: %f seconds elapsed'

    def __init__(self, log, start=None, stop=None):
        self.log = log
        self.stop = stop if stop else LogElapsedTime.stop
        self.start = start if start else LogElapsedTime.start
        super().__init__()

    def on_start(self):
        self.log(self.start)

    def on_stop(self):
        self.log(self.stop, self.elapsed)



class DebugElapsedTime(LogElapsedTime):

    def __init__(self, start=None, stop=None):
        super().__init__(log=logger.debug, start=start, stop=stop)


class InfoElapsedTime(LogElapsedTime):

    def __init__(self, start=None, stop=None):
        super().__init__(log=logger.info, start=start, stop=stop)


