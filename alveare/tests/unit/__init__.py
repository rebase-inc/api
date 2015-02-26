import unittest

from alveare.common.database import DB
from alveare import create_app

class AlveareTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(DB)
        self.db = DB
        self.app.test_request_context().push()
        DB.create_all()
        DB.session.commit()

        def cleanup():
            DB.session.remove()
            DB.drop_all()
            DB.get_engine(self.app).dispose()
        self.addCleanup(cleanup)
