from . import AlveareModelTestCase

from alveare.common.utils import validate_query_fn
from alveare.models import SkillSet
from alveare.tests.common.skill_set import (
    case_mgr,
    case_contractor,
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
            True, True, True, True
        )

