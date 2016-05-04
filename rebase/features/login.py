from flask import session, request
from flask.ext.login import LoginManager, AnonymousUserMixin

from rebase.models import User


class AnonymousUser(AnonymousUserMixin):

    admin = False

    def is_admin(self):
        return False
    
    def get_id(self):
        return None

    def allowed_to_get(self, instace):
        return False

    def allowed_to_create(self, instance):
        return isinstance(instance, User)

    def allowed_to_modify(self, instance):
        return False

    def allowed_to_delete(self, instance):
        return False


def setup_login(app):
    login_manager = LoginManager()
    login_manager.anonymous_user = AnonymousUser
    login_manager.session_protection = app.config['FLASK_LOGIN_SESSION_PROTECTION']
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        user = User.query.get(user_id)
        if 'role_id' in session:
            user.set_role(session['role_id'])
        else:
            session['role_id'] = user.set_role(int(request.cookies.get('role_id', 0))).id
        return user


