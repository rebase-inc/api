from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from rebase.models import User

def setup_admin(app, db_session):
    admin = Admin(app, name='Rebase', template_mode='bootstrap3')
    admin.add_view(ModelView(User, db_session))

