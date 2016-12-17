from http.server import BaseHTTPRequestHandler
from logging import getLogger


logger = getLogger()


class CacheBaseHandler(BaseHTTPRequestHandler):
    def log_error(self, message, *args):
        logger.error(message, *args)

    def log_message(self, message, *args):
        logger.info(message, *args)
