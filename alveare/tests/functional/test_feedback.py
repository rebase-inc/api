import unittest

from . import AlveareRestTestCase

from alveare.models import Feedback, Contractor, Manager

class TestFeedbackResource(AlveareRestTestCase):

    def test_get_all(self):
        self.login_admin()
        response = self.get_resource('feedbacks')
        self.assertIn('feedbacks', response)
        self.assertIsInstance(response['feedbacks'], list)
        self.assertIn('id', response['feedbacks'][0])
        self.assertIn('contractor', response['feedbacks'][0])
        self.assertIn('auction', response['feedbacks'][0])

    def test_get_one(self):
        self.login_admin()
        response = self.get_resource('feedbacks')
        feedback_id = response['feedbacks'][0]['id']

        response = self.get_resource('feedbacks/{}'.format(feedback_id))
        feedback = response['feedback']

        self.assertEqual(feedback.pop('id'), feedback_id)
        self.assertIsInstance(feedback.pop('comment').pop('id'), int)
        self.assertIsInstance(feedback.pop('contractor').pop('id'), int)
        self.assertIsInstance(feedback.pop('auction').pop('id'), int)
        self.assertEqual(feedback, {})

    def test_create_new(self):
        self.login_admin()
        ''' admin only '''
        user_data = dict(first_name='foo', last_name='bar', email='foo@bar.com', password='baz')
        user = self.post_resource('users', user_data)['user']
        contractor = self.post_resource('contractors', dict(user=user))['contractor']

        auction = self.get_resource('auctions')['auctions'][0]
        feedback_data = dict(auction=auction, contractor=contractor)

        feedback = self.post_resource('feedbacks', feedback_data)['feedback']
        self.assertIsInstance(feedback.pop('id'), int)
        self.assertEqual(feedback.pop('auction').pop('id'), auction['id'])
        self.assertEqual(feedback.pop('contractor').pop('id'), contractor['id'])
        self.assertEqual(feedback, {})

    def test_update(self):
        self.login_admin()
        user_data = dict(first_name='foo', last_name='bar', email='foo@bar.com', password='baz')
        user = self.post_resource('users', user_data)['user']
        contractor = self.post_resource('contractors', dict(user=user))['contractor']

        auction = self.get_resource('auctions')['auctions'][0]
        feedback_data = dict(auction=auction, contractor=contractor)

        feedback = self.post_resource('feedbacks', feedback_data)['feedback']
        updated_feedback = self.put_resource('feedbacks/{}'.format(feedback['id']), feedback)['feedback']


    def test_that_feedback_auction_owner_can_see(self):
        feedback = Feedback.query.first()
        manager_user = feedback.auction.organization.managers[0].user

        self.post_resource('auth', dict(user=dict(email=manager_user.email), password='foo'))
        self.get_resource('feedbacks/{}'.format(feedback.id))
        self.login_as_new_user()
        self.get_resource('feedbacks/{}'.format(feedback.id), 401)

    def test_that_creator_only_sees_feedbacks_that_they_made(self):
        random_contractor = Contractor.query.first()
        all_owned_feedback_ids = [feedback.id for feedback in random_contractor.feedbacks]

        self.post_resource('auth', dict(user=dict(email=random_contractor.user.email), password='foo'))
        feedbacks = self.get_resource('feedbacks')['feedbacks']
        response_feedback_ids = [feedback['id'] for feedback in feedbacks]
        self.assertEqual(set(all_owned_feedback_ids), set(response_feedback_ids))

    def test_that_manager_only_sees_feedbacks_that_they_own(self):
        random_manager = Manager.query.first()
        all_auctions = random_manager.organization.auctions
        all_owned_feedback_ids = []
        for auction in all_auctions:
            for feedback in auction.feedbacks:
                all_owned_feedback_ids.append(feedback.id)
        self.post_resource('auth', dict(user=dict(email=random_manager.user.email), password='foo'))
        feedbacks = self.get_resource('feedbacks')['feedbacks']
        response_feedback_ids = [feedback['id'] for feedback in feedbacks]
        self.assertEqual(set(all_owned_feedback_ids), set(response_feedback_ids))
