from atexit import register

from rebase.tests.database import delete_all_test_databases

register(delete_all_test_databases)

