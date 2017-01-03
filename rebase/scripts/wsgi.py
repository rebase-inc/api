import os
from multiprocessing import current_process

from werkzeug.contrib.fixers import ProxyFix

import rsyslog
from ..app import create


current_process().name = os.environ['HOSTNAME']
rsyslog.setup(log_level = os.environ['LOG_LEVEL'])
app = create(routes=True)
app.wsgi_app = ProxyFix(app.wsgi_app)

