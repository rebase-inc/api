from flask.ext.script import Command, Option

from alveare import create_app
from alveare.models import User
from alveare.common.database import DB

class CreateAdmin(Command):
    '''Creates a user and tag it as administrator'''

    option_list = (
        Option('email',  help='The email is used as the login.'),
        Option('password',  help='Make it long and hard to guess, duh.'),
        Option('--first', default='', help='First name.'),
        Option('--last', default='', help='Last name.'),
    )

    def run(self, email, password, first, last):
        user = User(first, last, email, password)
        user.admin = True
        app, _, DB = create_app()
        DB.session.add(user)
        DB.session.commit()
