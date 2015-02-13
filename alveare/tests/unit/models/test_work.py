from . import AlveareModelTestCase
from sqlalchemy.orm.exc import ObjectDeletedError

from alveare import models
from alveare.common import mock

class TestWorkModel(AlveareModelTestCase):
    model = models.Work

    def test_create(self):
        work = mock.create_some_work(self.db).pop()
        self.db.session.commit()

        found_work = self.model.query.get(work.id)
        self.assertIsInstance(found_work.offer.price, int)
        self.assertIsInstance(found_work.debit.price, int)
        self.assertIsInstance(found_work.credit.price, int)
        self.assertIsInstance(found_work.mediation_rounds.one(), models.Mediation)

    def test_delete(self):
        work = mock.create_some_work(self.db).pop()
        self.db.session.commit()

        review_id = work.review.id
        debit_id = work.debit.id
        credit_id = work.credit.id
        mediation_id = work.mediation_rounds.all()[0].id
        work_offer_id = work.offer.id
        arbitration_id = work.mediation_rounds.all()[0].arbitration.id

        self.assertNotEqual(self.model.query.get(work.id), None)
        self.delete_instance(self.model, work)

        self.assertEqual(models.Review.query.get(review_id), None)
        self.assertEqual(models.Debit.query.get(debit_id), None)
        self.assertEqual(models.Credit.query.get(credit_id), None)
        self.assertEqual(models.Mediation.query.get(mediation_id), None)
        self.assertEqual(models.WorkOffer.query.get(work_offer_id), None)
        self.assertEqual(models.Arbitration.query.get(arbitration_id), None)

    def test_update(self):
        work = mock.create_some_work(self.db).pop()
        self.db.session.commit()

        self.db.session.delete(work.review)
        self.db.session.delete(work.debit)
        self.db.session.delete(work.credit)
        for mediation_round in work.mediation_rounds.all():
            self.db.session.delete(mediation_round)
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
        self.assertEqual(found_work.review.rating, 4)
        self.assertEqual(found_work.debit.price, 100)
        self.assertEqual(found_work.credit.price, 110)
        self.assertEqual(len(found_work.mediation_rounds.all()), 2)
