from functools import partial
from http.server import HTTPServer, BaseHTTPRequestHandler
from logging import getLogger, Formatter
from logging.handlers import SysLogHandler
from multiprocessing import current_process, set_start_method
from pickle import dumps, loads
from queue import Empty
from signal import signal, SIGTERM, SIGQUIT, SIGINT
from sys import exit
from threading import Thread, current_thread

from ..cache.process import CacheProcess
from ..cache.request import CacheHandler
from ..common.config import Config
from ..common.log import setup


setup()


logger = getLogger(__name__)


def quit(sig, frame, server, processes):
    #logger.info('Shutting down child processes')
    server.shutdown()
    for process in processes.values():
        process.q.put({'action': 'cooldown'})
        process.join()
    #logger.info('All children are shutdown. Quitting')
    exit()


def refresh(processes):
    for role_id, process in processes.items():
        if not process.is_alive():
            del processes[role_id]
            

def main():
    current_process().name = 'Cache'
    current_thread().name = 'main'
    root_logger = getLogger()
    rsyslog = root_logger.handlers[0]
    # this format adds the thread name (cache is the only multithreaded component of our system)
    rsyslog.setFormatter(Formatter('%(levelname)s {%(processName)s[%(process)d] %(threadName)s} %(message)s'))
    processes = dict()
    server = HTTPServer(('0.0.0.0', 5000), CacheHandler)
    _quit = partial(quit, server=server, processes=processes)
    signal(SIGTERM, _quit)
    signal(SIGQUIT, _quit)
    signal(SIGINT, _quit)
    ip, port = server.server_address

    server_thread = Thread(name='http', target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    logger.info('HTTP server is listening at {}:{}'.format(ip, port))

    while True:
        try:
            task = CacheHandler.q.get(timeout=10)
        except Empty as e:
            # processes may timeout if no action is sent to them for a while,
            # so we need to keep the 'processes' dict up-to-date
            refresh(processes)
            continue
        #logger.debug('Received task: {}'.format(task))
        CacheHandler.q.task_done()
        refresh(processes)
        _id  = task['id']
        if _id == 0:
            # broadcast to all children
            for process in processes.values():
                process.q.put(task)
            continue
        if _id not in processes:
            # create a new child process for this role
            processes[_id] = CacheProcess(_id)
            logger.debug('Processes: {}'.format(processes))
        processes[_id].q.put(task)


if __name__ == '__main__':
    set_start_method('spawn')
    main()