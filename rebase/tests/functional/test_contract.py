from . import RebaseRestTestCase, PermissionTestCase
from rebase.common.utils import RebaseResource, ids
from rebase.models import Contract, Bid, Contractor, Manager
from rebase.tests.common.contract import (
    case_user_1_as_mgr,
    case_user_1_as_contractor,
    case_user_2_as_mgr,
    case_user_2_as_contractor,
    case_admin,
    case_admin_collection,
)


class TestContract(PermissionTestCase):
    model = 'Contract'

    def new(self, old_contract):
        return {
            'bid': {
                'id': old_contract.bid.id,
                'work_offers': [ids(offer) for offer in old_contract.bid.work_offers],
            }
        }

    def validate_view(self, contract):
        self.assertTrue(contract)
        self.assertTrue(contract.pop('id'))
        self.assertTrue(contract.pop('bid'))
        self.assertEqual(contract, {})

    def update(self, contract):
        updated_contract = ids(contract)
        # what else could we update?
        return updated_contract

    def test_user_1_as_mgr_collection(self):
        self.collection(case_user_1_as_mgr, 'manager')

    def test_user_1_as_mgr_view(self):
        self.view(case_user_1_as_mgr, 'manager', True)

    def test_user_1_as_mgr_modify(self):
        self.modify(case_user_1_as_mgr, 'manager', False)

    def test_user_1_as_mgr_delete(self):
        self.delete(case_user_1_as_mgr, 'manager', False)

    def test_user_1_as_mgr_create(self):
        self.create(case_user_1_as_mgr, 'manager', False)

    def test_user_1_as_contractor_collection(self):
        self.collection(case_user_1_as_contractor, 'contractor')

    def test_user_1_as_contractor_view(self):
        self.view(case_user_1_as_contractor, 'contractor', True)

    def test_user_1_as_contractor_modify(self):
        self.modify(case_user_1_as_contractor, 'contractor', False)

    def test_user_1_as_contractor_delete(self):
        self.delete(case_user_1_as_contractor, 'contractor', False)

    def test_user_1_as_contractor_create(self):
        self.create(case_user_1_as_contractor, 'contractor', False)

    def test_user_2_as_mgr_collection(self):
        self.collection(case_user_2_as_mgr, 'manager')

    def test_user_2_as_mgr_view(self):
        self.view(case_user_2_as_mgr, 'manager', True)

    def test_user_2_as_mgr_modify(self):
        self.modify(case_user_2_as_mgr, 'manager', False)

    def test_user_2_as_mgr_delete(self):
        self.delete(case_user_2_as_mgr, 'manager', False)

    def test_user_2_as_mgr_create(self):
        self.create(case_user_2_as_mgr, 'manager', False)

    def test_user_2_as_contractor_collection(self):
        self.collection(case_user_2_as_contractor, 'contractor')

    def test_user_2_as_contractor_view(self):
        self.view(case_user_2_as_contractor, 'contractor', True)

    def test_user_2_as_contractor_modify(self):
        self.modify(case_user_2_as_contractor, 'contractor', False)

    def test_user_2_as_contractor_delete(self):
        self.delete(case_user_2_as_contractor, 'contractor', False)

    def test_user_2_as_contractor_create(self):
        self.create(case_user_2_as_contractor, 'contractor', False)

    def test_admin_collection(self):
        self.collection(case_admin_collection, 'manager')

    def test_admin_view(self):
        self.view(case_admin, 'contractor', True)

    def test_admin_modify(self):
        self.modify(case_admin, 'contractor', True)

    def test_admin_delete(self):
        self.delete(case_admin, 'contractor', True)

    def test_admin_create(self):
        self.create(case_admin, 'contractor', True)


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
        self.login(creator_user.email, 'foo', role='contractor')
        self.get_resource('contracts/{}'.format(contract.id))

    def test_that_bid_auction_owner_can_see(self):
        contract = Contract.query.first()
        manager_user = contract.bid.auction.organization.managers[0].user

        self.login(manager_user.email, 'foo', role='manager')
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
        self.login(random_manager.user.email, 'foo', role='manager')
        contracts = self.get_resource('contracts')['contracts']
        response_contract_ids = [contract['id'] for contract in contracts]
        self.assertEqual(set(all_owned_bid_contract_ids), set(response_contract_ids))

