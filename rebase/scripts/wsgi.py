from multiprocessing import current_process

from werkzeug.contrib.fixers import ProxyFix

from ..app import create
from ..common.log import setup


current_process().name = 'API Web Worker'


setup()


app = create(routes=True)


app.wsgi_app = ProxyFix(app.wsgi_app)


