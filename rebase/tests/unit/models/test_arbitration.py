import unittest

from . import RebaseModelTestCase
from rebase import models
from rebase.common import mock

class TestArbitrationModel(RebaseModelTestCase):

    def test_create(self):
        arbitration = mock.create_some_work(self.db).pop().mediations[0].arbitration
        self.db.session.commit()

        self.assertIsInstance(arbitration.mediation.work.offer.price, int)

    def test_delete(self):
        arbitration = mock.create_some_work(self.db).pop().mediations[0].arbitration
        self.db.session.commit()
        self.delete_instance(arbitration)
        self.assertEqual(models.Arbitration.query.get(arbitration.id), None)

    @unittest.skip("arbitration has no updatable fields yet")
    def test_update(self):
        arbitration = self.create_arbitration()
        self.db.session.commit()

        arbitration.outcome = 4
        self.db.session.commit()

        modified_arbitration = models.Arbitration.query.get(arbitration.id)
        self.assertEqual(modified_arbitration.outcome, 4)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(models.Arbitration, 'foo')
