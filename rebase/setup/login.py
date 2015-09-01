from flask import session, abort
from flask.ext.login import LoginManager

from rebase.common.exceptions import NoRole
from rebase.models import User

class AnonymousUser(object):
    is_active = False
    def is_authenticated(self): return False
    def is_anonymous(self): return True
    def get_id(self): return None
    def allowed_to_get(self, instace): return False
    def allowed_to_create(self, instance): return isinstance(instance, User)
    def allowed_to_modify(self, instance): return False
    def allowed_to_delete(self, instance): return False

def setup_login(app):
    login_manager = LoginManager()
    login_manager.anonymous_user = AnonymousUser
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return None
        role = user.roles.first()
        if not role:
            # should be redirect(url_for('pick_a_role')) 
            raise NoRole(user)
        user.current_role = role
        session['role_id'] = role.id
        session['role'] = role.type

        return user
