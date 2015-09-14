import atexit
from os import getpid, environ
from subprocess import check_output, check_call, call
from unittest import TestCase

from rebase import create_app
from rebase.common.database import DB

TEST_DATABASE_PREFIX='rebase_test'
DB_URL_PREFIX='postgresql://localhost'

def all_databases():
    output = check_output(['psql', '-lqt']).decode(encoding='UTF-8').splitlines()
    return map(lambda line: line.lstrip().partition(' ')[0], output)

def all_test_databases():
    return filter(lambda database_name: database_name.startswith(TEST_DATABASE_PREFIX), all_databases())

def exists(db_name):
    return any(map(lambda database_name: database_name.startswith(db_name), all_databases()))

@atexit.register
def delete_all_test_databases():
    DB.session.close_all()
    for test_db in all_test_databases():
        call(['dropdb', test_db])

def make_one_test_database_for_this_process():
    db_name = '{}_{}'.format(TEST_DATABASE_PREFIX, getpid())
    test_url='{}/{}'.format(DB_URL_PREFIX, db_name)
    if not exists(db_name):
        #print(db_name+' does not exists, let\'s create it.')
        check_call(['createdb', db_name])
        environ['TEST_URL'] = test_url
    else:
        #print(db_name+' already exists.')
        pass

class RebaseTestCase(TestCase):

    def setUp(self):
        make_one_test_database_for_this_process()
        self.app, self.app_context, self.db = create_app(testing=True)
        self.db.create_all()
        self.db.session.commit()

        def cleanup():
            self.db.session.remove()
            self.db.session.close_all()
            self.db.drop_all()
            self.db.get_engine(self.app).dispose()
        self.addCleanup(cleanup)
