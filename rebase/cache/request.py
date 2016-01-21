from http.server import BaseHTTPRequestHandler
import logging
from queue import Queue
import re

def route(action):
    return re.compile(r'/(?P<action>{action})/(?P<role_id>[0-9]+)'.format(action=action))

routes = (
    route('warmup'),
    route('cooldown')
)

class CacheBaseHandler(BaseHTTPRequestHandler):
    def log_error(self, message, *args):
        logging.error(message, *args)

    def log_message(self, message, *args):
        logging.info(message, *args)


class CacheHandler(CacheBaseHandler):
    q = Queue()
    def do_POST(self):
        match = None
        for route in routes:
            match = route.match(self.path)
            if match:
                break
        if match:
            self.send_response(200)
            self.end_headers()
            task = {
                'id': int(match.group('role_id'), 0),
                'action': match.group('action')
            }
            logging.debug('Sending {} to main thread'.format(task))
            self.q.put(task)
        else:
            self.send_response(404)
            self.end_headers()

