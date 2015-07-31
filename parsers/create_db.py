from alveare import create_app
from alveare.common.database import DB_PRODUCTION_NAME, DB_TEST_NAME
from sqlalchemy import create_engine

def add_parser(subparsers):
    create_db_parser = subparsers.add_parser('create_db', help='Create the database on which the website will run.')
    create_db_parser.set_defaults(func=create_db)
    create_db_parser.add_argument('--test', action='store_true', help='Only create a test database.')

def create_db(args):
    engine = create_engine("postgres:///template1")
    conn = engine.connect()
    conn.execute('commit')
    if args.test:
        DB_NAME = DB_TEST_NAME
    else:
        DB_NAME = DB_PRODUCTION_NAME
    conn.execute('create database '+DB_NAME)
    conn.close()

    app, _, DB = create_app(db_name=DB_NAME)
    if not args.test:
        DB.create_all()
        DB.session.commit()
