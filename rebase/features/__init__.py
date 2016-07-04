from rebase.common.database import DB

from .cors import setup_cors
from .login import setup_login
from .logger import setup_logger
from .rq import setup_rq
from .cache import setup_cache

def install(app):
    setup_cors(app)
    setup_login(app)
    setup_rq(app)
    setup_logger(app)
    setup_cache(app)
