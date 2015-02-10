import unittest

from . import AlveareModelTestCase

from alveare import models

class TestCodeRepositoryModel(AlveareModelTestCase):
    model = models.CodeRepository

    def test_create(self):
        new_code_repository = self.create_model(self.model)

    def test_delete(self):
        new_code_repository = self.create_model(self.model)
        self.delete_instance(self.model, new_code_repository)

    @unittest.skip('CodeRepository model doesnt have any updatable fields yet')
    def test_update(self):
        new_code_repository = self.create_model(self.model)

    @unittest.skip('CodeRepository model doesnt have any creation fields yet')
    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(self.model, 'foo', 2)
        with self.assertRaises(ValueError):
            self.create_model(self.model, 1234, 2)
        with self.assertRaises(ValueError):
            self.create_model(self.model, 123456789, 'foo')

