import json
import time
import copy

from . import RebaseRestTestCase
from rebase.models import Review

class TestReviewResource(RebaseRestTestCase):

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

    def test_contractor_can_get_their_own(self):
        review = Review.query.first()
        contractor = review.work.offer.contractor
        self.get_resource('reviews/{}'.format(review.id), 401)
        self.login(contractor.user.email, 'foo')
        self.get_resource('reviews/{}'.format(review.id))

        returned_reviews = self.get_resource('reviews')['reviews']
        returned_review_ids = [r['id'] for r in returned_reviews]
        actual_review_ids = []
        for work_offer in contractor.work_offers:
            if work_offer.work and work_offer.work.review:
                actual_review_ids.append(work_offer.work.review.id)
        self.assertEqual(set(returned_review_ids), set(actual_review_ids))

        self.login_as_new_user()
        reviews = self.get_resource('reviews')['reviews']
        review_ids = [r['id'] for r in reviews]
        self.assertNotIn(review.id, review_ids)

    def test_manager_of_auction_can_see_them(self):
        review = Review.query.first()
        manager = review.work.offer.bid.auction.organization.managers[0]
        self.login(manager.user.email, 'foo')
        self.get_resource('reviews/{}'.format(review.id))
        reviews = self.get_resource('reviews')['reviews']
        review_ids = [r['id'] for r in reviews]
        self.assertIn(review.id, review_ids)

        self.login_as_new_user()
        self.get_resource('reviews/{}'.format(review.id), 401)
        reviews = self.get_resource('reviews')['reviews']
        review_ids = [r['id'] for r in reviews]
        self.assertNotIn(review.id, review_ids)


