from alveare import create_app
from alveare.models import User
from alveare.common.database import DB

def add_parser(subparsers):
    parser = subparsers.add_parser('create_admin')
    parser.set_defaults(func=create_admin)
    parser.add_argument('email')
    parser.add_argument('password')
    parser.add_argument('--first', default='', help='First name of this admin')
    parser.add_argument('--last', default='', help='Last name of this admin')

def create_admin(args):
    user = User(
        args.first,
        args.last,
        args.email,
        args.password
    )
    user.admin = True
    app, _, DB = create_app()
    DB.session.add(user)
    DB.session.commit()
