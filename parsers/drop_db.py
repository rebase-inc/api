from alveare.common.database import DB_PRODUCTION_NAME, DB_TEST_NAME
from sqlalchemy import create_engine

def add_parser(subparsers):
    drop_db_parser = subparsers.add_parser('drop_db')
    drop_db_parser.set_defaults(func=drop_db)
    drop_db_parser.add_argument('--test', action='store_true', help='Only delete the test database.')

def drop_db(args):
    engine = create_engine("postgres:///template1")
    conn = engine.connect()
    conn.execute('commit')
    if args.test:
        DB_NAME = DB_TEST_NAME
    else:
        DB_NAME = DB_PRODUCTION_NAME
    conn.execute('drop database '+DB_NAME)
    conn.close()
