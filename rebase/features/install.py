
from .cors import setup_cors
from .login import setup_login
from .rq import setup_rq
from .cache import setup_cache


def install(app):
    setup_cors(app)
    setup_login(app)
    setup_rq(app)
    setup_cache(app)


