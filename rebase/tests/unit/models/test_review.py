from . import RebaseModelTestCase

from rebase import models
from rebase.common import mock

class TestReviewModel(RebaseModelTestCase):

    def test_create(self):
        review = mock.create_one_work_review(self.db, mock.create_one_user(self.db), 3, 'Hello')
        self.db.session.commit()

        found_review = models.Review.query.get(review.id)
        self.assertEqual(found_review.work.id, review.work.id)
        self.assertEqual(found_review.rating, 3)
        self.assertEqual(found_review.comments.one().content, 'Hello')

    def test_delete(self):
        review = mock.create_one_work_review(self.db, mock.create_one_user(self.db), 2, 'Hello')
        self.db.session.commit()

        found_review = models.Review.query.get(review.id)
        self.db.session.delete(found_review)
        self.db.session.commit()

        self.assertEqual(models.Review.query.get(review.id), None)

    def test_delete_comment(self):
        review = mock.create_one_work_review(self.db, mock.create_one_user(self.db), 2, 'Bye')
        self.db.session.commit()

        self.delete_instance(review.comments.one())
        self.assertNotEqual(models.Review.query.get(review.id), None)

    def test_update(self):
        review = mock.create_one_work_review(self.db, mock.create_one_user(self.db), 3, 'foo')
        self.db.session.commit()

        found_review = models.Review.query.get(review.id)
        self.assertEqual(found_review.rating, 3)
        self.assertEqual(found_review.work.id, review.work.id)

        found_review.rating = 4
        self.db.session.commit()

        found_again_review = models.Review.query.get(review.id)
        self.assertEqual(found_review.rating, 4)

    def test_bad_create(self):
        self.assertRaises(ValueError, mock.create_one_work_review, self.db, mock.create_one_user(self.db), 'foo', 'foo')
        self.assertRaises(ValueError, mock.create_one_work_review, self.db, mock.create_one_user(self.db), -1, 'foo')
        self.assertRaises(ValueError, mock.create_one_work_review, self.db, mock.create_one_user(self.db), 6, 'foo')
