from . import AlveareModelTestCase

from rebase.common.utils import validate_query_fn
from rebase.models import SkillSet
from rebase.tests.common.skill_set import (
    case_mgr,
    case_contractor,
    case_admin,
)

class TestSkillSet(AlveareModelTestCase):
    def test_mgr(self):
        validate_query_fn(
            self,
            SkillSet,
            case_mgr,
            SkillSet.as_manager,
            False, False, False, True
        )

    def test_contractor(self):
        validate_query_fn(
            self,
            SkillSet,
            case_contractor,
            SkillSet.as_contractor,
            False, False, False, True
        )

    def test_admin(self):
        user, resource = case_admin(self.db)
        expected_resources = [resource]
        resources = SkillSet.query_by_user(user).all()
        self.assertEqual(expected_resources, resources)
        self.assertEqual(expected_resources, SkillSet.query_by_user(user).all())
        self.assertEqual(True, bool(resource.allowed_to_be_created_by(user)))
        self.assertEqual(True, bool(resource.allowed_to_be_modified_by(user)))
        self.assertEqual(True, bool(resource.allowed_to_be_deleted_by(user)))
        self.assertEqual(True, bool(resource.allowed_to_be_viewed_by(user)))
