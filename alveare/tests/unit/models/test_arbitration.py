import unittest

from . import AlveareModelTestCase
from alveare import models

class TestArbitrationModel(AlveareModelTestCase):
    model = models.Arbitration

    def test_create_arbitration(self):
        new_arbitration = self.create_model(self.model, 1)
        self.assertEqual(new_arbitration.outcome, 1)

    def test_delete_arbitration(self):
        new_arbitration = self.create_model(self.model, 2)
        self.assertEqual(new_arbitration.outcome, 2)
        self.delete_instance(self.model, new_arbitration)

    def test_update_arbitration(self):
        new_arbitration = self.create_model(self.model, 3)
        self.assertEqual(new_arbitration.outcome, 3)

        new_arbitration.outcome = 4
        self.db.session.commit()

        modified_arbitration = self.model.query.get(new_arbitration.id)
        self.assertEqual(modified_arbitration.outcome, 4)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(self.model, 'foo')
