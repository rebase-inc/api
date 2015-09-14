from rebase.common.database import DB

from .admin import setup_admin
from .cache import setup_cache
from .cors import setup_cors
from .login import setup_login
from .rq import setup_rq

def install(app):
    setup_cors(app)
    setup_admin(app, DB.session)
    setup_login(app)
    setup_rq(app)
    setup_cache(app)

