import os

from flask import send_from_directory

def register_home(app):
    @app.route('/')
    def login_root():
        return send_from_directory(os.path.abspath('../react-app/'), 'index.html', cache_timeout=None)
