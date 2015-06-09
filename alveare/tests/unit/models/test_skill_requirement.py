from . import AlveareModelTestCase

from alveare.common.utils import validate_query_fn
from alveare.models import SkillRequirement
from alveare.tests.common.skill_requirement import (
    case_mgr,
    case_contractor,
    case_admin,
)

class TestSkillRequirement(AlveareModelTestCase):
    def test_mgr(self):
        validate_query_fn(
            self,
            SkillRequirement,
            case_mgr,
            SkillRequirement.get_all,
            False, False, False, True
        )

    def test_contractor(self):
        validate_query_fn(
            self,
            SkillRequirement,
            case_contractor,
            SkillRequirement.get_all,
            False, False, False, False
        )


    def test_admin(self):
        user, resource = case_admin(self.db)
        expected_resources = [resource]
        resources = SkillRequirement.query_by_user(user).all()
        self.assertEqual(expected_resources, resources)
        self.assertEqual(expected_resources, SkillRequirement.query_by_user(user).all())
        self.assertEqual(True, bool(resource.allowed_to_be_created_by(user)))
        self.assertEqual(True, bool(resource.allowed_to_be_modified_by(user)))
        self.assertEqual(True, bool(resource.allowed_to_be_deleted_by(user)))
        self.assertEqual(True, bool(resource.allowed_to_be_viewed_by(user)))
