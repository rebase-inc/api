from . import AlveareModelTestCase

from alveare.models import SkillSet
from alveare.common.mock import create_one_contractor

class TestSkillSetModel(AlveareModelTestCase):
    def test_create(self):
        contractor = create_one_contractor(self.db)
        self.db.session.commit()
        self.assertNotEqual(SkillSet.query.get(contractor.id), None)

    def test_delete(self):
        contractor = create_one_contractor(self.db)
        self.db.session.commit()
        self.delete_instance(contractor)
        self.assertEqual(SkillSet.query.all(), [])

