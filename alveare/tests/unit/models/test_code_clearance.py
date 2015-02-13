from sqlalchemy.exc import StatementError

from . import AlveareModelTestCase

from alveare import models

class TestCodeClearanceModel(AlveareModelTestCase):
    model = models.CodeClearance

    def test_create(self):
        new_code_clearance = self.create_model(self.model, True)
        self.assertEqual(new_code_clearance.pre_approved, True)

    def test_delete(self):
        new_code_clearance = self.create_model(self.model, False)
        self.assertEqual(new_code_clearance.pre_approved, False)
        self.delete_instance(new_code_clearance)

    def test_update(self):
        new_code_clearance = self.create_model(self.model, True)
        self.assertEqual(new_code_clearance.pre_approved, True)

        new_code_clearance.pre_approved = False
        self.db.session.commit()

        modified_code_clearance = self.model.query.get(new_code_clearance.id)
        self.assertEqual(modified_code_clearance.pre_approved, False)

    def test_bad_create(self):
        with self.assertRaises(StatementError):
            self.create_model(self.model, 'foo')

