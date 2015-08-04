import json
import time
import copy

from . import RebaseRestTestCase

from rebase.models import Work

class TestWorkResource(RebaseRestTestCase):

    def test_get_all(self):
        self.login_admin()
        response = self.get_resource('work')
        self.assertIn('work', response)
        self.assertIsInstance(response['work'], list)

    def test_get_one(self):
        self.login_admin()
        response = self.get_resource('work')
        work_id = response['work'][0]['id']

        response = self.get_resource('work/{}'.format(work_id))
        work = response['work']
        self.assertIsInstance(work.pop('id'), int)
        self.assertIsInstance(work.pop('state'), str)
        self.assertIsInstance(work.pop('review'), dict)
        #self.assertIn('state', work.pop('mediation')[0])

    def test_contractor_can_get_their_own(self):
        work = Work.query.first()
        contractor = work.offer.contractor
        self.get_resource('work/{}'.format(work.id), 401)
        self.login(contractor.user.email, 'foo')
        self.get_resource('work/{}'.format(work.id))

        returned_works = self.get_resource('work')['work']
        returned_work_ids = [w['id'] for w in returned_works]
        actual_work_ids = [wo.work.id for wo in contractor.work_offers if wo.work]
        self.assertEqual(set(returned_work_ids), set(actual_work_ids))

        self.login_as_new_user()
        works = self.get_resource('work')['work']
        work_ids = [w['id'] for w in works]
        self.assertNotIn(work.id, work_ids)

    def test_manager_of_auction_can_see_them(self):
        work = Work.query.first()
        manager = work.offer.bid.auction.organization.managers[0]
        self.login(manager.user.email, 'foo')
        self.get_resource('work/{}'.format(work.id))
        works = self.get_resource('work')['work']
        work_ids = [w['id'] for w in works]
        self.assertIn(work.id, work_ids)

        self.login_as_new_user()
        self.get_resource('work/{}'.format(work.id), 401)
        works = self.get_resource('work')['work']
        work_ids = [w['id'] for w in works]
        self.assertNotIn(work.id, work_ids)

    def test_update(self):
        self.login_admin()
        work = Work.query.filter(Work.state == 'in_progress').first()

        state = self.post_resource('work/{}/halt_events'.format(work.id), dict(reason='you suck'))['work']['state']
        self.assertEqual(state, 'blocked')

        state = self.post_resource('work/{}/resume_events'.format(work.id))['work']['state']
        self.assertEqual(state, 'in_progress')

        state = self.post_resource('work/{}/review_events'.format(work.id))['work']['state']
        self.assertEqual(state, 'in_review')

        state = self.post_resource('work/{}/complete_events'.format(work.id))['work']['state']
        self.assertEqual(state, 'complete')
