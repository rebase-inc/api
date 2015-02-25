import datetime

from sqlalchemy.orm.exc import ObjectDeletedError

from . import AlveareModelTestCase
from alveare import models
from alveare.common import mock
from alveare.common.state import MACHINES

class TestMediationModel(AlveareModelTestCase):

    def test_state(self):
        mediation = mock.create_some_work(self.db).pop().mediation_rounds.one()
        mediation_id = mediation.id
        self.db.session.commit()

        mediation.machine.send('dev_answer')
        MACHINES.process_all_events()
        self.assertEqual(mediation.state, 'waiting_for_client')

        mediation.machine.send('timeout')
        MACHINES.process_all_events()
        self.assertEqual(mediation.state, 'timed_out')

        mediation.machine.send('timeout_answer')
        MACHINES.process_all_events()
        self.assertEqual(mediation.state, 'decision')

        mediation.machine.send('agree')
        MACHINES.process_all_events()
        self.assertEqual(mediation.state, 'agreement')
        self.db.session.commit()
        self.db.session.close()

        found_mediation = models.Mediation.query.get(mediation_id)
        self.assertEqual(found_mediation.state, 'agreement')


    def test_create_mediation(self):
        mediation = mock.create_some_work(self.db).pop().mediation_rounds.one()
        self.db.session.commit()

        found_mediation = models.Mediation.query.get(mediation.id)
        self.assertIsInstance(found_mediation.work.offer.price, int)

    def test_delete_mediation(self):
        mediation = mock.create_some_work(self.db).pop().mediation_rounds.one()
        self.db.session.commit()
        arbitration_id = mediation.arbitration.id

        self.assertNotEqual(models.Mediation.query.get(mediation.id), None)

        self.delete_instance(mediation)

        self.assertEqual(models.Mediation.query.get(mediation.id), None)

        self.assertEqual(models.Arbitration.query.get(arbitration_id), None)

    def test_update_mediation(self):
        mediation = mock.create_some_work(self.db).pop().mediation_rounds.one()
        self.db.session.commit()

        found_mediation = models.Mediation.query.get(mediation.id)
        new_timeout = datetime.datetime.now() + datetime.timedelta(days = 4)
        found_mediation.timeout = new_timeout

        found_again_mediation = models.Mediation.query.get(mediation.id)
        self.assertEqual(found_again_mediation.timeout, new_timeout)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(models.Mediation, 'foo')
