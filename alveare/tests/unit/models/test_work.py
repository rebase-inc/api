from . import AlveareModelTestCase
from sqlalchemy.orm.exc import ObjectDeletedError

from alveare import models

class TestWorkModel(AlveareModelTestCase):
    model = models.Work

    def test_create(self):
        ticket_snap = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snap, 100)
        work = self.create_model(self.model, work_offer)
        self.assertEqual(work.offer.price, 100)
        _ = models.Review(work, 4)
        _ = models.Debit(work, 100)
        _ = models.Credit(work, 110)
        _ = models.Mediation(work)
        _ = models.Mediation(work)
        self.db.session.commit()
        found_work = self.model.query.get(work.id)
        self.assertEqual(found_work.offer.price, 100)
        self.assertEqual(found_work.debit.price, 100)
        self.assertEqual(found_work.credit.price, 110)
        self.assertEqual(len(found_work.mediation_rounds.all()), 2)

    def test_delete(self):
        ticket_snap = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snap, 100)
        work = self.create_model(self.model, work_offer)
        review = models.Review(work, 4)
        debit = models.Debit(work, 100)
        credit = models.Credit(work, 110)
        mediation = models.Mediation(work)
        arbitration = models.Arbitration(mediation)
        self.db.session.commit()
        self.assertNotEqual(self.model.query.get(work.id), None)

        self.delete_instance(self.model, work)

        with self.assertRaises(ObjectDeletedError):
            models.Review.query.get(review.id)
        with self.assertRaises(ObjectDeletedError):
            models.Debit.query.get(debit.id)
        with self.assertRaises(ObjectDeletedError):
            models.Credit.query.get(credit.id)
        with self.assertRaises(ObjectDeletedError):
            models.Mediation.query.get(mediation.id)
        with self.assertRaises(ObjectDeletedError):
            models.WorkOffer.query.get(work_offer.id)
        with self.assertRaises(ObjectDeletedError):
            models.Arbitration.query.get(arbitration.id)

    def test_update(self):
        ticket_snap = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snap, 100)
        work = self.create_model(self.model, work_offer)
        self.assertEqual(work.offer.price, 100)
        review = models.Review(work, 4)
        debit = models.Debit(work, 100)
        credit = models.Credit(work, 110)
        mediation1 = models.Mediation(work)
        mediation2 = models.Mediation(work)
        self.db.session.commit()
        found_work = self.model.query.get(work.id)
        self.assertEqual(found_work.offer.price, 100)
        self.assertEqual(found_work.debit.price, 100)
        self.assertEqual(found_work.credit.price, 110)
        self.assertEqual(len(found_work.mediation_rounds.all()), 2)

        self.db.session.delete(review)
        self.db.session.delete(debit)
        self.db.session.delete(credit)
        self.db.session.delete(mediation1)
        self.db.session.delete(mediation2)
        self.db.session.commit()

        found_work = self.model.query.get(work.id)
        self.assertEqual(found_work.review, None)
        self.assertEqual(found_work.debit, None)
        self.assertEqual(found_work.credit, None)
        self.assertEqual(len(found_work.mediation_rounds.all()), 0)

        _ = models.Review(work, 4)
        _ = models.Debit(work, 100)
        _ = models.Credit(work, 110)
        _ = models.Mediation(work)
        _ = models.Mediation(work)
        self.db.session.commit()
        found_work = self.model.query.get(work.id)
        self.assertEqual(found_work.offer.price, 100)
        self.assertEqual(found_work.debit.price, 100)
        self.assertEqual(found_work.credit.price, 110)
        self.assertEqual(len(found_work.mediation_rounds.all()), 2)

    def test_bad_create(self):
        ticket_snap = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snap, 100)
        with self.assertRaises(ValueError):
            self.create_model(self.model, 'foobar')
        work = self.create_model(self.model, work_offer)
        _ = models.Review(work, 4)
        _ = models.Debit(work, 100)
        _ = models.Credit(work, 110)
        _ = models.Mediation(work)
        _ = models.Mediation(work)
        with self.assertRaises(ValueError):
            _ = models.Review(work, 5)
        with self.assertRaises(ValueError):
            _ = models.Debit(work, 130)
        with self.assertRaises(ValueError):
            _ = models.Credit(work, 190)
