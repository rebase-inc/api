import unittest

from . import AlveareRestTestCase

class TestFeedbackResource(AlveareRestTestCase):

    def test_get_all(self):
        self.login_admin()
        response = self.get_resource('feedbacks')
        self.assertIn('feedbacks', response)
        self.assertIsInstance(response['feedbacks'], list)
        self.assertIn('id', response['feedbacks'][0])
        self.assertIn('message', response['feedbacks'][0])
        self.assertIn('contractor', response['feedbacks'][0])
        self.assertIn('auction', response['feedbacks'][0])

    def test_get_one(self):
        self.login_admin()
        response = self.get_resource('feedbacks')
        feedback_id = response['feedbacks'][0]['id']

        response = self.get_resource('feedbacks/{}'.format(feedback_id))
        feedback = response['feedback']

        self.assertEqual(feedback.pop('id'), feedback_id)
        self.assertIsInstance(feedback.pop('message'), str)
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
        feedback_data = dict(auction=auction, contractor=contractor, message='blah blah blah')

        feedback = self.post_resource('feedbacks', feedback_data)['feedback']
        self.assertIsInstance(feedback.pop('id'), int)
        self.assertEqual(feedback.pop('auction').pop('id'), auction['id'])
        self.assertEqual(feedback.pop('contractor').pop('id'), contractor['id'])
        self.assertEqual(feedback.pop('message'), 'blah blah blah')
        self.assertEqual(feedback, {})

    def test_update(self):
        self.login_admin()
        user_data = dict(first_name='foo', last_name='bar', email='foo@bar.com', password='baz')
        user = self.post_resource('users', user_data)['user']
        contractor = self.post_resource('contractors', dict(user=user))['contractor']

        auction = self.get_resource('auctions')['auctions'][0]
        feedback_data = dict(auction=auction, contractor=contractor, message='blah blah blah')

        feedback = self.post_resource('feedbacks', feedback_data)['feedback']
        feedback['message'] = 'halb halb halb'
        updated_feedback = self.put_resource('feedbacks/{}'.format(feedback['id']), feedback)['feedback']

        self.assertEqual(updated_feedback.pop('message'), feedback['message'])

