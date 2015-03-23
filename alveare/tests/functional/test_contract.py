from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip

class TestContractResource(AlveareRestTestCase):
    def setUp(self):
        self.resource = AlveareResource(self, 'Contract')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        contract = self.resource.get_any()
        self.assertTrue(contract)
        self.assertTrue(contract.pop('id'))
        self.assertEqual(contract, {})

    @skip('contracts are immutable')
    def test_update(self):
        self.login_admin()
        pass

    def test_delete(self):
        self.login_admin()
        self.resource.delete_any()

    def test_delete_auction(self):
        self.login_admin()
        contract = self.resource.get_any()
        self.delete_resource('bids/{}'.format(contract['id']))
        self.get_resource(self.resource.url(contract), 404)
