from multiprocessing import current_process
from unittest import TestCase

from rebase.app import create
import rebase.tests.database.cleanup

from ..common.log import setup

setup()

current_process().name = 'Unit Tests'


class RebaseTestCase(TestCase):

    def setUp(self):
        import rebase.tests.database.create
        self.app, self.app_context, self.db = create(testing=True)
        self.db.create_all()
        self.db.session.commit()

        def cleanup():
            self.db.session.remove()
            self.db.session.close_all()
            self.db.drop_all()
            self.db.get_engine(self.app).dispose()
        self.addCleanup(cleanup)
