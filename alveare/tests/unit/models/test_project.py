import unittest

from sqlalchemy.orm.exc import ObjectDeletedError

from . import AlveareModelTestCase

from alveare import models
from alveare.common import mock

class TestProjectModel(AlveareModelTestCase):

    def test_create(self):
        project = mock.create_one_project(self.db, 'Alveare', 'api')
        self.db.session.commit()

        self.assertEqual(project.name, 'api')
        self.assertEqual(project.organization.name, 'Alveare')
        self.assertNotEqual(project.code_repository, None)

    def test_delete(self):
        project = mock.create_one_project(self.db, 'Alveare', 'api')
        self.db.session.commit()

        org_id = project.organization.id
        repo_id = project.code_repository.id

        self.assertEqual(project.name, 'api')
        self.assertEqual(project.organization.name, 'Alveare')
        self.assertNotEqual(project.code_repository, None)

        self.delete_instance(models.Project, project)

        self.assertEqual(models.Organization.query.get(org_id).name, 'Alveare')
        self.assertEqual(models.CodeRepository.query.get(repo_id), None)

    #@unittest.skip('Project model doesnt have any updatable fields yet')
    #def test_update(self):
        #return

    #@unittest.skip('Project model doesnt have any creation fields yet')
    #def test_bad_create(self):
        #return

