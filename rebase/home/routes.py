import os
from logging import getLogger

from flask import send_from_directory, request

logger = getLogger()

def register_home(app):
    @app.route('/')
    def login_root():
        # note this is only used in dev mode.
        # in production, Nginx serves static content
        logger.debug('Headers: %s', request.headers)
        return send_from_directory(os.path.abspath('../react-app/'), 'index.html', cache_timeout=None)
