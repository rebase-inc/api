import unittest

from . import AlveareModelTestCase
from alveare import models

class TestArbitrationModel(AlveareModelTestCase):
    model = models.Arbitration

    def test_create_arbitration(self):
        ticket_snap = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snap, 100)
        work = self.create_model(models.Work, work_offer)
        mediation = self.create_model(models.Mediation, work)
        arbitration = self.create_model(self.model, mediation)
        self.assertEqual(arbitration.mediation.work.offer.price, 100)

    def test_delete_arbitration(self):
        ticket_snap = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snap, 100)
        work = self.create_model(models.Work, work_offer)
        mediation = self.create_model(models.Mediation, work)
        arbitration = self.create_model(self.model, mediation)
        self.delete_instance(self.model, arbitration)

    @unittest.skip("arbitration has no updatable fields yet")
    def test_update_arbitration(self):
        ticket_snap = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snap, 100)
        work = self.create_model(models.Work, work_offer)
        mediation = self.create_model(models.Mediation, work)
        arbitration = self.create_model(self.model, mediation)

        arbitration.outcome = 4
        self.db.session.commit()

        modified_arbitration = self.model.query.get(arbitration.id)
        self.assertEqual(modified_arbitration.outcome, 4)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(self.model, 'foo')
