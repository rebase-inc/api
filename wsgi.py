from werkzeug.contrib.fixers import ProxyFix

from rebase.app import create

app = create()
app.wsgi_app = ProxyFix(app.wsgi_app)
