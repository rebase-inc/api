from copy import copy

from . import RebaseRestTestCase, PermissionTestCase
from rebase.models import Work
from rebase.common.database import ids
from rebase.tests.common.work import WorkUseCase

class TestWorkResource(RebaseRestTestCase):

    def test_get_all(self):
        self.login_admin()
        response = self.get_resource('works')
        self.assertIn('works', response)
        self.assertIsInstance(response['works'], list)

    def test_get_one(self):
        self.login_admin()
        response = self.get_resource('works')
        work_id = response['works'][0]['id']

        response = self.get_resource('works/{}'.format(work_id))
        work = response['work']
        self.assertIsInstance(work.pop('id'), int)
        self.assertIsInstance(work.pop('state'), str)
        self.assertIsInstance(work.pop('review'), dict)
        #self.assertIn('state', work.pop('mediation')[0])

    def test_contractor_can_get_their_own(self):
        work = Work.query.first()
        contractor = work.offer.contractor
        self.get_resource('works/{}'.format(work.id), 401)
        self.login(contractor.user.email, 'foo')
        self.get_resource('works/{}'.format(work.id))

        returned_works = self.get_resource('works')['works']
        returned_work_ids = [w['id'] for w in returned_works]
        actual_work_ids = [wo.work.id for wo in contractor.work_offers if wo.work]
        self.assertEqual(set(returned_work_ids), set(actual_work_ids))

        self.login_as_new_user()
        works = self.get_resource('works')['works']
        work_ids = [w['id'] for w in works]
        self.assertNotIn(work.id, work_ids)

    def test_manager_of_auction_can_see_them(self):
        work = Work.query.first()
        manager = work.offer.bid.auction.organization.managers[0]
        self.login(manager.user.email, 'foo')
        self.get_resource('works/{}'.format(work.id))
        works = self.get_resource('works')['works']
        work_ids = [w['id'] for w in works]
        self.assertIn(work.id, work_ids)

        self.login_as_new_user()
        self.get_resource('works/{}'.format(work.id), 401)
        works = self.get_resource('works')['works']
        work_ids = [w['id'] for w in works]
        self.assertNotIn(work.id, work_ids)

    def test_update(self):
        self.login_admin()
        work = Work.query.filter(Work.state == 'in_progress').first()

        state = self.post_resource('works/{}/halt'.format(work.id), dict(reason='you suck'))['work']['state']
        self.assertEqual(state, 'blocked')

        state = self.post_resource('works/{}/resume'.format(work.id))['work']['state']
        self.assertEqual(state, 'in_progress')

        state = self.post_resource('works/{}/review'.format(work.id))['work']['state']
        self.assertEqual(state, 'in_review')

        state = self.post_resource('works/{}/complete'.format(work.id))['works']['state']
        self.assertEqual(state, 'complete')


class TestWork(PermissionTestCase):
    model = 'Work'

    def setUp(self):
        super().setUp()
        self.case = WorkUseCase()

    def validate_view(self, work):
        _work = copy(work)
        self.assertIsInstance(_work.pop('id'), int)
        self.assertIsInstance(_work.pop('state'), str)
        self.assertIsInstance(_work.pop('offer'), dict)

    def update(_, work):
        updated_work = ids(work)
        #updated_work.update(rating=(work.rating+1)%5)
        return updated_work

    def new(_, old_instance):
        return {
            'offer': ids(instance.offer),
        }

    def test_work_blocked(self):
        user_1, user_2, work, work_2 = self.case.base_scenario(self.db)
        self.login(user_2.email, 'foo', 'contractor')
        work_obj = self.resource.get(ids(work))
        self.validate_view(work_obj)
        self.assertIn('state', work_obj)
        self.assertEqual(work_obj['state'], 'in_progress')

        ##### halt_work
        work_obj = self.post_resource(
            'works/{}/halt'.format(work.id),
            dict(reason='Flat tyre'),
        )['work']
        self.assertEqual(work_obj['state'], 'blocked')

        ##### resume_work
        work_obj = self.post_resource(
            'works/{}/resume'.format(work.id),
            {},
        )['work']
        self.assertEqual(work_obj['state'], 'in_progress')

    def test_work_halt_event_malformed(self):
        _, user_2, work, _ = self.case.base_scenario(self.db)
        self.login(user_2.email, 'foo', 'contractor')
        work_obj = self.resource.get(ids(work))
        self.validate_view(work_obj)
        self.assertIn('state', work_obj)
        self.assertEqual(work_obj['state'], 'in_progress')

        ##### halt_work
        response = self.post_resource(
            'works/{}/halt'.format(work.id),
            {}, # missing 'reason' field
            expected_code = 400
        )

    def test_bogus_work(self):
        _, user_2, work, _ = self.case.base_scenario(self.db)
        self.login(user_2.email, 'foo', 'contractor')
        response = self.resource.get({'id': 0}, expected_status=404)

    def _test_send_event_to_bogus_work(self, event, event_data):
        _, user_2, work, _ = self.case.base_scenario(self.db)
        self.login(user_2.email, 'foo', 'contractor')
        work_obj = self.resource.get(ids(work))
        self.validate_view(work_obj)
        self.assertIn('state', work_obj)
        self.assertEqual(work_obj['state'], 'in_progress')

        ##### halt_work
        response = self.post_resource(
            'works/{}/{}'.format(0, event),
            event_data,
            expected_code = 404
        )

    def test_send_halt_to_bogus_work(self):
        self._test_send_event_to_bogus_work('halt', {'reason': 'yo mama too big!'})

    def test_send_review_to_bogus_work(self):
        self._test_send_event_to_bogus_work('review', {})

    def test_send_mediate_to_bogus_work(self):
        self._test_send_event_to_bogus_work('mediate', {})

    def test_send_complete_to_bogus_work(self):
        self._test_send_event_to_bogus_work('complete', {})

    def test_send_resume_to_bogus_work(self):
        self._test_send_event_to_bogus_work('resume', {})

    def test_send_fail_to_bogus_work(self):
        self._test_send_event_to_bogus_work('fail', {})
