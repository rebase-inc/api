import unittest

from . import AlveareModelTestCase
from alveare import models

class TestArbitrationModel(AlveareModelTestCase):

    def test_create_arbitration(self):
        arbitration = self.create_arbitration()
        self.db.session.commit()

        self.assertIsInstance(arbitration.mediation.work.offer.price, int)

    def test_delete_arbitration(self):
        arbitration = self.create_arbitration()
        self.db.session.commit()
        self.delete_instance(models.Arbitration, arbitration)
        self.assertEqual(models.Arbitration.query.get(arbitration.id), None)

    @unittest.skip("arbitration has no updatable fields yet")
    def test_update_arbitration(self):
        arbitration = self.create_arbitration()
        self.db.session.commit()

        arbitration.outcome = 4
        self.db.session.commit()

        modified_arbitration = models.Arbitration.query.get(arbitration.id)
        self.assertEqual(modified_arbitration.outcome, 4)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(models.Arbitration, 'foo')
