from . import AlveareRestTestCase
from alveare.common.resource import AlveareResource
from unittest import skip


class TestProjectResource(AlveareRestTestCase):
    def setUp(self):
        self.r = AlveareResource(self, 'project')
        super().setUp()

    def test_get_one(self):
        project = self.r.get_any()
        self.assertTrue(project) # mock should have created at least one account
        self.assertTrue(project['id'])

    def test_delete(self):
        self.r.delete_any()

    def test_delete_organization(self):
        project = self.r.get_any()
        self.delete_resource('organizations/{}'.format(project['organization_id']))
        self.get_resource(self.r.url(project), 404)
