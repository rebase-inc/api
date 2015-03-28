import json
import time
import copy

from . import AlveareRestTestCase

class TestReviewResource(AlveareRestTestCase):

    def test_get_all(self):
        self.login_admin()
        response = self.get_resource('reviews')
        self.assertIn('reviews', response)
        self.assertIsInstance(response['reviews'], list)

    def test_get_one(self):
        self.login_admin()
        response = self.get_resource('reviews')
        review_id = response['reviews'][0]['id']

        response = self.get_resource('reviews/{}'.format(review_id))
        review = response['review']
        self.assertIsInstance(review.pop('id'), int)
        self.assertIsInstance(review.pop('rating'), int)
        self.assertIsInstance(review.pop('comments'), list)
        self.assertIsInstance(review.pop('work'), int)

    def test_create_new(self):
        self.login_admin()
        response = self.get_resource('work')

        #find a work object without a review
        work = [work for work in response['work'] if 'review' not in work][0]

        review = dict(rating=4, work={'id': work['id']})
        review = self.post_resource('reviews', review)['review']

        self.assertIsInstance(review.pop('id'), int)
        self.assertEqual(review.pop('comments'), [])
        self.assertEqual(review.pop('rating'), 4)
        self.assertEqual(review.pop('work'), work['id'])

    def test_update(self):
        self.login_admin()
        response = self.get_resource('reviews')
        review_id = response['reviews'][0]['id']

        response = self.get_resource('reviews/{}'.format(review_id))
        review = response['review']
        new_rating = dict(rating=review['rating'] % 5 + 1)
        response = self.put_resource('reviews/{}'.format(review['id']), new_rating)
        review.update(new_rating)
        self.assertEqual(review, response['review'])


