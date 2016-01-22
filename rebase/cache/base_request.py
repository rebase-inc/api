from http.server import BaseHTTPRequestHandler
from logging import error, info


class CacheBaseHandler(BaseHTTPRequestHandler):
    def log_error(self, message, *args):
        error(message, *args)

    def log_message(self, message, *args):
        info(message, *args)
