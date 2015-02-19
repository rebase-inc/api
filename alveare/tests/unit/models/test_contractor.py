import unittest
import datetime

from . import AlveareModelTestCase

from alveare import models
from alveare.common import mock

class TestContractorModel(AlveareModelTestCase):

    def test_create(self):
        contractor = mock.create_one_contractor(self.db)
        _ = models.RemoteWorkHistory(contractor)
        self.db.session.commit()
        contractor = models.Contractor.query.get(contractor.id)
        self.assertIsInstance(contractor.user, models.User)
        self.assertIsInstance(contractor.skill_set, models.SkillSet)
        self.assertIsInstance(contractor.remote_work_history, models.RemoteWorkHistory)
        self.assertIsInstance(contractor.skill_set, models.SkillSet)

    def test_delete_contract(self):
        contractor = mock.create_one_contractor(self.db)
        _ = models.RemoteWorkHistory(contractor)
        self.db.session.commit()

        contractor_id = contractor.id
        user_id = contractor.user.id
        skill_set_id = contractor.skill_set.id
        remote_work_history_id = contractor.remote_work_history.id

        found_contractor = models.Contractor.query.get(contractor_id)
        self.delete_instance(found_contractor)

        self.assertEqual(models.Contractor.query.get(contractor_id), None)
        self.assertIsInstance(models.User.query.get(user_id), models.User)
        self.assertEqual(models.SkillSet.query.get(skill_set_id), None)
        self.assertEqual(models.RemoteWorkHistory.query.get(remote_work_history_id), None)

    @unittest.skip('Contractor model doesnt have any updatable fields yet')
    def test_update(self):
        contract = self.create_model(self.model)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            contractor = models.Contractor('foo')
            SkillSet(contractor)
            self.db.session.add(contractor)
        with self.assertRaises(ValueError):
            contractor = models.Contractor(2)
            SkillSet(contractor)
            self.db.session.add(contractor)

