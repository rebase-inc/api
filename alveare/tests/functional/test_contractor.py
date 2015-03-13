from . import AlveareRestTestCase
from alveare.common.resource import AlveareResource
from unittest import skip


class TestContractorResource(AlveareRestTestCase):
    def setUp(self):
        self.r = AlveareResource(self, 'contractor')
        super().setUp()

    def test_get_one(self):
        contractor = self.r.get_any()
        self.assertTrue(contractor) # mock should have created at least one account
        self.assertTrue(contractor['id'])

    def test_create(self):
        user = AlveareResource(self, 'user').get_any()
        user.pop('last_seen')
        user.pop('email')
        self.r.create(
            user =  user
        )

    def test_update(self):
        contractor = self.r.get_any()
        contractor['busyness'] = 123
        self.r.update(**contractor) 

    def test_delete(self):
        self.r.delete_any()

    def test_delete_user(self):
        contractor = self.r.get_any()
        self.delete_resource('users/{}'.format(contractor['user']['id']))
        self.get_resource(self.r.url(contractor), 404)
