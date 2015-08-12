import unittest

from rebase import create_app

class RebaseTestCase(unittest.TestCase):

    def setUp(self):
        self.app, self.app_context, self.db = create_app(testing=True)
        self.db.create_all()
        self.db.session.commit()

        def cleanup():
            self.db.session.remove()
            self.db.drop_all()
            self.db.get_engine(self.app).dispose()
        self.addCleanup(cleanup)
