import unittest

from . import AlveareModelTestCase

from alveare import models

class TestCodeRepositoryModel(AlveareModelTestCase):

    def test_create(self):
        self.create_code_repository()

    def test_delete(self):
        repo = self.create_code_repository()
        self.db.session.commit()

        self.delete_instance(models.CodeRepository, repo)
        self.assertEqual(models.CodeRepository.query.get(repo.id), None)

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

