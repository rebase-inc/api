from sqlalchemy.exc import StatementError

from . import AlveareModelTestCase

from alveare import models
from alveare.common import mock

class TestCodeClearanceModel(AlveareModelTestCase):

    def test_create(self):
        code_clearance = mock.create_one_code_clearance(self.db)
        self.db.session.commit()
        found_clearance = models.CodeClearance.query.get(code_clearance.id)
        self.assertIsInstance(found_clearance.project, models.Project)
        self.assertIsInstance(found_clearance.contractor, models.Contractor)

    def test_delete(self):
        code_clearance = mock.create_one_code_clearance(self.db)
        self.db.session.commit()
        code_clearance_id = code_clearance.id
        project_id = code_clearance.project.id
        contractor_id = code_clearance.contractor.id
        self.delete_instance(code_clearance)
        self.assertEqual(models.CodeClearance.query.get(code_clearance_id), None)
        self.assertNotEqual(models.Project.query.get(project_id), None)
        self.assertNotEqual(models.Contractor.query.get(contractor_id), None)

    def test_delete_project(self):
        code_clearance = mock.create_one_code_clearance(self.db)
        self.db.session.commit()
        code_clearance_id = code_clearance.id
        project_id = code_clearance.project.id
        contractor_id = code_clearance.contractor.id
        self.delete_instance(code_clearance.project)
        self.assertFalse(models.CodeClearance.query.get(code_clearance_id))
        self.assertFalse(models.Project.query.get(project_id))
        self.assertTrue(models.Contractor.query.get(contractor_id))

    def test_delete_contractor(self):
        code_clearance = mock.create_one_code_clearance(self.db)
        self.db.session.commit()
        code_clearance_id = code_clearance.id
        project_id = code_clearance.project.id
        contractor_id = code_clearance.contractor.id
        self.delete_instance(code_clearance.contractor)
        self.assertFalse(models.CodeClearance.query.get(code_clearance_id))
        self.assertTrue(models.Project.query.get(project_id))
        self.assertFalse(models.Contractor.query.get(contractor_id))

    def test_update(self):
        code_clearance = mock.create_one_code_clearance(self.db)
        self.db.session.commit()
        new_preapproved = not code_clearance.pre_approved
        code_clearance.pre_approved = new_preapproved
        self.db.session.commit()

        found_clearance = models.CodeClearance.query.get(code_clearance.id)
        self.assertEqual(found_clearance.pre_approved, new_preapproved)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            code_clearance = self.create_model(models.CodeClearance, 'foo', 'bar')
            self.db.session.add(code_clearance)

