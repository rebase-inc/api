from copy import copy
from logging import error, info

from flask.ext.login import login_user

from rebase.models import Role

class Proxy(Role):
    def __init__(self):
        pass

    def init(self, obj):
        self.__dict__.update(copy(obj.__dict__))

ROLE=Proxy()

def init_role(role_id):
    info('Loading Role(%d)', role_id)
    ROLE.init(Role.query.get(role_id))
    if not ROLE:
        error('Unknown role, terminating')
        return
    ROLE.user.set_role(ROLE.id)
    login_user(ROLE.user)
