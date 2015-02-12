import datetime

from sqlalchemy.orm.exc import ObjectDeletedError

from . import AlveareModelTestCase
from alveare import models

class TestMediationModel(AlveareModelTestCase):

    def test_create_mediation(self):
        work_offer = models.WorkOffer(100)
        work = self.create_model(models.Work, work_offer)
        mediation = self.create_model(models.Mediation, work)

        found_mediation = models.Mediation.query.get(mediation.id)
        self.assertEqual(found_mediation.work.offer.price, 100)

    def test_delete_mediation(self):
        work_offer = models.WorkOffer(100)
        work = self.create_model(models.Work, work_offer)
        mediation = self.create_model(models.Mediation, work)
        arbitration = self.create_model(models.Arbitration, mediation)

        self.delete_instance(models.Mediation, mediation)
        self.assertEqual(models.Mediation.query.get(mediation.id), None)

        with self.assertRaises(ObjectDeletedError):
            models.Arbitration.query.get(arbitration.id)

    def test_update_mediation(self):
        work_offer = models.WorkOffer(100)
        work = self.create_model(models.Work, work_offer)
        mediation = self.create_model(models.Mediation, work)

        found_mediation = models.Mediation.query.get(mediation.id)
        self.assertEqual(found_mediation.work.offer.price, 100)

        new_timeout = datetime.datetime.now() + datetime.timedelta(days = 4)
        found_mediation.timeout = new_timeout

        found_again_mediation = models.Mediation.query.get(mediation.id)
        self.assertEqual(found_again_mediation.timeout, new_timeout)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(models.Mediation, 'foo')
