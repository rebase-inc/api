from os import getpid, environ
from subprocess import check_output, check_call, call


TEST_DATABASE_PREFIX='rebase_test'
DB_URL_PREFIX='postgresql://localhost'

def all_databases():
    output = check_output(['psql', '-lqt']).decode(encoding='UTF-8').splitlines()
    return map(lambda line: line.lstrip().partition(' ')[0], output)

def all_test_databases():
    return filter(lambda database_name: database_name.startswith(TEST_DATABASE_PREFIX), all_databases())

def exists(db_name):
    return any(map(lambda database_name: database_name.startswith(db_name), all_databases()))

def delete_all_test_databases():
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
