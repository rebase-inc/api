from multiprocessing import current_process

from werkzeug.contrib.fixers import ProxyFix

import rsyslog
from ..app import create


current_process().name = 'API Web Worker'
rsyslog.setup()
app = create(routes=True)
app.wsgi_app = ProxyFix(app.wsgi_app)

