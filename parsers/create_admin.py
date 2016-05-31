from flask.ext.script import Command, Option

from rebase.app import create
from rebase.common.database import DB
from rebase.models import User

class CreateAdmin(Command):
    '''Creates a user and tags it as administrator'''

    option_list = (
        Option('email',  help='The email is used as the login.'),
        Option('password',  help='Make it long and hard to guess, duh.'),
        Option('--first', default='', help='First name.'),
        Option('--last', default='', help='Last name.'),
    )

    def run(self, email, password, first, last):
        user = User(first, last, email, password)
        user.admin = True
        app = create()
        DB.session.add(user)
        DB.session.commit()
