import unittest

from rebase.common.database import DB, DB_TEST_NAME
from rebase import create_app

class RebaseTestCase(unittest.TestCase):

    def setUp(self):
        self.app, self.app_context, self.db = create_app(testing=True)
        DB.create_all()
        DB.session.commit()

        def cleanup():
            DB.session.remove()
            DB.drop_all()
            DB.get_engine(self.app).dispose()
        self.addCleanup(cleanup)
