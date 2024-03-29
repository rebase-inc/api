import unittest
import datetime

from . import RebaseModelTestCase

from rebase import models
from rebase.common import mock
from rebase.tests.common.contractor import (
    case_cleared_contractors,
    case_cleared_contractors_as_contractor,
    case_nominated_contractors,
)

class TestContractorModel(RebaseModelTestCase):

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

    def _test_get_contractors(self, query_fn, case_fn):
        user, expected_contractors = case_fn(self.db)
        case_fn(self.db) # more unrelated data, to make sure query_fn is selective enough
        contractors = query_fn(user).all()
        self.assertTrue(contractors)
        self.assertEqual(len(contractors), len(expected_contractors))
        for contractor in expected_contractors:
            self.assertIn(contractor, contractors)

    def test_as_mgr_get_cleared_contractors(self):
        self._test_get_contractors(
            models.Contractor.as_manager_get_cleared_contractors,
            case_cleared_contractors
        )
        self._test_get_contractors(
            models.Contractor.get_all,
            case_cleared_contractors
        )

    def test_as_mgr_get_nominated_contractors(self):
        self._test_get_contractors(
            models.Contractor.as_manager_get_nominated_contractors,
            case_nominated_contractors
        )
        self._test_get_contractors(
            models.Contractor.get_all,
            case_nominated_contractors
        )

    def test_as_contractor_get_cleared_contractors(self):
        self._test_get_contractors(
            models.Contractor.as_contractor_get_cleared_contractors,
            case_cleared_contractors_as_contractor
        )
        self._test_get_contractors(
            models.Contractor.get_all,
            case_cleared_contractors_as_contractor
        )
