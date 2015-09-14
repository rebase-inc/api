from unittest import TestCase

from rebase import create_app

class RebaseTestCase(TestCase):

    def setUp(self):
        import rebase.tests.database
        self.app, self.app_context, self.db = create_app(testing=True)
        self.db.create_all()
        self.db.session.commit()

        def cleanup():
            self.db.session.remove()
            self.db.session.close_all()
            self.db.drop_all()
            self.db.get_engine(self.app).dispose()
        self.addCleanup(cleanup)
