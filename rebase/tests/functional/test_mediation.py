from datetime import timedelta

from . import RebaseRestTestCase

from . import PermissionTestCase
from rebase.common.utils import ids
from rebase.models import Mediation
from rebase.tests.common.mediation import MediationUseCase

class TestMediation(PermissionTestCase):
    model = 'Mediation'

    def setUp(self):
        super().setUp()
        self.case = MediationUseCase()

    def new(_, old_instance):
        return {
            'work': ids(old_instance.work),
            'timeout': old_instance.timeout.isoformat()
        }

    def update(_, mediation):
        updated_mediation = ids(mediation)
        updated_mediation.update(timeout=(mediation.timeout + timedelta(days=3)).isoformat())
        return updated_mediation

    def validate_modify(_, test_resource, requested, returned):
        # TODO re-implement with datetime comparison
        pass

    def validate_view(self, mediation):
        self.assertIsInstance(mediation.pop('id'), int)
        self.assertIsInstance(mediation.pop('timeout'), str)
        self.assertIsInstance(mediation.pop('state'), str)
        #self.assertIsInstance(mediation.pop('work'), int)
        #self.assertIsInstance(mediation.pop('comments'), dict)
        
    def test_user_1_as_mgr_collection(self):
        self.collection(self.case.user_1_as_mgr, 'manager')

    def test_user_1_as_mgr_view(self):
        self.view(self.case.user_1_as_mgr, 'manager', True)

    def test_user_1_as_mgr_modify(self):
        self.modify(self.case.user_1_as_mgr, 'manager', False)

    def test_user_1_as_mgr_delete(self):
        self.delete(self.case.user_1_as_mgr, 'manager', False)

    def test_user_1_as_mgr_create(self):
        self.create(self.case.user_1_as_mgr, 'manager', False)

    def test_user_1_as_contractor_collection(self):
        self.collection(self.case.user_1_as_contractor, 'contractor')

    def test_user_1_as_contractor_view(self):
        self.view(self.case.user_1_as_contractor, 'contractor', True)

    def test_user_1_as_contractor_modify(self):
        self.modify(self.case.user_1_as_contractor, 'contractor', False)

    def test_user_1_as_contractor_delete(self):
        self.delete(self.case.user_1_as_contractor, 'contractor', False)

    def test_user_1_as_contractor_create(self):
        self.create(self.case.user_1_as_contractor, 'contractor', False, delete_first=True)

    def test_user_2_as_mgr_collection(self):
        self.collection(self.case.user_2_as_mgr, 'manager')

    def test_user_2_as_mgr_view(self):
        self.view(self.case.user_2_as_mgr, 'manager', True)

    def test_user_2_as_mgr_modify(self):
        self.modify(self.case.user_2_as_mgr, 'manager', False)

    def test_user_2_as_mgr_delete(self):
        self.delete(self.case.user_2_as_mgr, 'manager', False)

    def test_user_2_as_mgr_create(self):
        self.create(self.case.user_2_as_mgr, 'manager', False, delete_first=True)

    def test_user_2_as_contractor_collection(self):
        self.collection(self.case.user_2_as_contractor, 'contractor')

    def test_user_2_as_contractor_view(self):
        self.view(self.case.user_2_as_contractor, 'contractor', True)

    def test_user_2_as_contractor_modify(self):
        self.modify(self.case.user_2_as_contractor, 'contractor', False)

    def test_user_2_as_contractor_delete(self):
        self.delete(self.case.user_2_as_contractor, 'contractor', False)

    def test_user_2_as_contractor_create(self):
        self.create(self.case.user_2_as_contractor, 'contractor', False, delete_first=True)

    def test_admin_collection(self):
        self.collection(self.case.admin_collection, 'manager')

    def test_admin_view(self):
        self.view(self.case.admin, 'contractor', True)

    def test_admin_modify(self):
        self.modify(self.case.admin, 'contractor', True)

    def test_admin_delete(self):
        self.delete(self.case.admin, 'contractor', True)

    def test_admin_create(self):
        self.create(self.case.admin, 'contractor', True, delete_first=True)


class TestMediationResource(RebaseRestTestCase):

    def test_get_all(self):
        self.login_admin()
        response = self.get_resource('mediations')
        self.assertIn('mediations', response)
        self.assertIsInstance(response['mediations'], list)

    def test_get_one(self):
        self.login_admin()
        response = self.get_resource('mediations')
        mediation_id = response['mediations'][0]['id']

        response = self.get_resource('mediations/{}'.format(mediation_id))
        mediation = response['mediation']
        self.assertIsInstance(mediation.pop('id'), int)
        self.assertIsInstance(mediation.pop('work'), int)
        self.assertIsInstance(mediation.pop('timeout'), str)
        self.assertIsInstance(mediation.pop('state'), str)

        if 'arbitration' in mediation:
            mediation.pop('arbitration')

        self.assertEqual(mediation.pop('comments'), [])
        self.assertEqual(mediation, {})

    def test_create_new(self):
        self.login_admin()
        ''' admin only '''
        response = self.get_resource('work')

        work = [work for work in response['work'] if not work['mediation']][0]

        mediation = dict(work={'id': work.get('id')})
        response = self.post_resource('mediations', mediation)
        mediation = response['mediation']

        self.assertIsInstance(mediation.pop('id'), int)
        self.assertIsInstance(mediation.pop('state'), str)
        self.assertIsInstance(mediation.pop('timeout'), str) #TODO: Actually check that this is a string
        self.assertEqual(mediation.pop('work'), work.get('id'))
        self.assertEqual(mediation.pop('comments'), [])
        self.assertEqual(mediation, {})

    def test_update(self):
        self.login_admin()
        ''' admin only '''
        response = self.get_resource('mediations')
        mediation_id = response['mediations'][0]['id']

        response = self.get_resource('mediations/{}'.format(mediation_id))
        mediation = response['mediation']
        new_state = dict(state = 'discussion' if mediation.get('state') != 'discussion' else 'waiting_for_client')
        if new_state.get('state') == 'waiting_for_client':
            new_state['dev_answer'] = 'in_progress'
        response = self.put_resource('mediations/{}'.format(mediation_id), new_state)
        mediation.update(new_state)
        self.assertEqual(mediation, response['mediation'])

    def test_contractor_can_get_their_own(self):
        mediation = Mediation.query.first()
        contractor = mediation.work.offer.contractor
        self.get_resource('mediations/{}'.format(mediation.id), 401)
        self.login(contractor.user.email, 'foo')
        self.get_resource('mediations/{}'.format(mediation.id))

        returned_mediations = self.get_resource('mediations')['mediations']
        returned_mediation_ids = [m['id'] for m in returned_mediations]
        actual_mediation_ids = []
        for work_offer in contractor.work_offers:
            if work_offer.work and work_offer.work.mediation_rounds:
                for mediation_round in work_offer.work.mediation_rounds:
                    actual_mediation_ids.append(mediation_round.id)
        self.assertEqual(set(returned_mediation_ids), set(actual_mediation_ids))

        self.login_as_new_user()
        mediations = self.get_resource('mediations')['mediations']
        mediation_ids = [m['id'] for m in mediations]
        self.assertNotIn(mediation.id, mediation_ids)

    def test_manager_of_auction_can_see_them(self):
        mediation = Mediation.query.first()
        manager = mediation.work.offer.bid.auction.organization.managers[0]
        self.login(manager.user.email, 'foo')
        self.get_resource('mediations/{}'.format(mediation.id))
        mediations = self.get_resource('mediations')['mediations']
        mediation_ids = [m['id'] for m in mediations]
        self.assertIn(mediation.id, mediation_ids)

        self.login_as_new_user()
        self.get_resource('mediations/{}'.format(mediation.id), 401)
        mediations = self.get_resource('mediations')['mediations']
        mediation_ids = [m['id'] for m in mediations]
        self.assertNotIn(mediation.id, mediation_ids)

