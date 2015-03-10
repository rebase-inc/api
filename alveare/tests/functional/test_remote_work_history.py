from . import AlveareRestTestCase
from alveare.common.resource import AlveareResource
from unittest import skip


class TestRemoteWorkHistoryResource(AlveareRestTestCase):
    def setUp(self):
        self.r = AlveareResource(self, 'remote_work_history')
        super().setUp()

    def test_get_one(self):
        rwh = self.r.get_any()
        self.assertTrue(rwh) # mock should have created at least one account
        self.assertTrue(rwh['id'])

    def test_create(self):
        contractor = AlveareResource(self, 'contractor').get_any()
        new_rwh = self.r.create(
            id=contractor['id']
        ) 

    def test_delete(self):
        self.r.delete_any()

    def test_delete_contractor(self):
        rwh = self.r.get_any()
        self.delete_resource('contractors/{}'.format(rwh['id']))
        self.get_resource(self.r.url(rwh), 404)

    #TODO add more tests to add/remove github accounts to a RWH
