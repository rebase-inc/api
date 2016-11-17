from werkzeug.contrib.fixers import ProxyFix

from ..app import create
from ..common.log import setup


setup()


app = create(routes=True)


app.wsgi_app = ProxyFix(app.wsgi_app)


