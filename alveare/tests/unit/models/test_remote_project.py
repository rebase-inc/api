import unittest

from sqlalchemy.orm.exc import ObjectDeletedError

from . import AlveareModelTestCase

from alveare import models
from alveare.common import mock

class TestRemoteProjectModel(AlveareModelTestCase):

    def test_create(self):
        remote_project = mock.create_one_remote_project(self.db, 'Alveare', 'api')
        self.db.session.commit()

        self.assertEqual(remote_project.name, 'api')
        self.assertEqual(remote_project.organization.name, 'Alveare')
        self.assertNotEqual(remote_project.code_repository, None)

    def test_delete(self):
        remote_project = mock.create_one_remote_project(self.db, 'Alveare', 'api')
        self.db.session.commit()

        org_id = remote_project.organization.id
        repo_id = remote_project.code_repository.id

        self.assertEqual(remote_project.name, 'api')
        self.assertEqual(remote_project.organization.name, 'Alveare')
        self.assertNotEqual(remote_project.code_repository, None)

        self.delete_instance(remote_project)

        self.assertEqual(models.Organization.query.get(org_id).name, 'Alveare')
        self.assertEqual(models.CodeRepository.query.get(repo_id), None)

    #@unittest.skip('RemoteProject model doesnt have any updatable fields yet')
    #def test_update(self):
        #return

    #@unittest.skip('RemoteProject model doesnt have any creation fields yet')
    #def test_bad_create(self):
        #return

