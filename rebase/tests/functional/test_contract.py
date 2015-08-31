from . import RebaseRestTestCase
from rebase.common.utils import RebaseResource
from unittest import skip

from rebase.models import Contract, Bid, Contractor, Manager

class TestContractResource(RebaseRestTestCase):
    def setUp(self):
        self.resource = RebaseResource(self, 'Contract')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        contract = self.resource.get_any()
        self.assertTrue(contract)
        self.assertTrue(contract.pop('id'))
        self.assertTrue(contract.pop('bid'))
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

    def test_that_bid_creator_can_see(self):
        contract = Contract.query.first()
        creator_user = contract.bid.contractor.user

        self.get_resource('contracts/{}'.format(contract.id), 401)
        self.post_resource('auth', dict(user=dict(email=creator_user.email), password='foo'))
        self.get_resource('contracts/{}'.format(contract.id))

    def test_that_bid_auction_owner_can_see(self):
        contract = Contract.query.first()
        manager_user = contract.bid.auction.organization.managers[0].user

        self.post_resource('auth', dict(user=dict(email=manager_user.email), password='foo'))
        self.get_resource('contracts/{}'.format(contract.id))
        self.login_as_new_user()
        self.get_resource('contracts/{}'.format(contract.id), 401)

    def test_that_creator_only_sees_bids_that_they_made(self):
        random_contractor = Contractor.query.first()
        all_owned_contract_ids = [bid.contract.id for bid in random_contractor.bids]

        self.login(random_contractor.user.email, 'foo')
        contracts = self.get_resource('contracts')['contracts']
        response_contract_ids = [contract['id'] for contract in contracts]
        self.assertEqual(set(all_owned_contract_ids), set(response_contract_ids))

    def test_that_manager_only_sees_bids_that_they_own(self):
        random_manager = Manager.query.first()
        all_auctions = random_manager.organization.auctions
        all_owned_bid_contract_ids = []
        for auction in all_auctions:
            for bid in auction.bids:
                all_owned_bid_contract_ids.append(bid.contract.id)
        self.post_resource('auth', dict(user=dict(email=random_manager.user.email), password='foo'))
        contracts = self.get_resource('contracts')['contracts']
        response_contract_ids = [contract['id'] for contract in contracts]
        self.assertEqual(set(all_owned_bid_contract_ids), set(response_contract_ids))

