import unittest

from alveare.common.database import DB, DB_TEST_NAME
from alveare import create_app

class AlveareTestCase(unittest.TestCase):

    def setUp(self):
        self.app, self.app_context, self.db = create_app(local=True, db_name=DB_TEST_NAME)
        DB.create_all()
        DB.session.commit()

        def cleanup():
            DB.session.remove()
            DB.drop_all()
            DB.get_engine(self.app).dispose()
        self.addCleanup(cleanup)
