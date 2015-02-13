from . import AlveareModelTestCase

from alveare import models

class TestReviewModel(AlveareModelTestCase):

    def test_create(self):
        review = self.create_review(3, comment = 'Hello')

        found_review = models.Review.query.get(review.id)
        self.assertEqual(found_review.work.id, review.work.id)
        self.assertEqual(found_review.rating, 3)
        self.assertEqual(found_review.comments.one().content, 'Hello')

    def test_delete(self):
        review = self.create_review(2)

        found_review = models.Review.query.get(review.id)
        self.db.session.delete(found_review)
        self.db.session.commit()

        self.assertEqual(models.Review.query.get(review.id), None)

    def test_delete_comment(self):
        review = self.create_review(4, comment = 'Bye')
        self.delete_instance(models.Comment, review.comment)
        self.assertNotEqual(models.Review.query.get(review.id), None)

    def test_update(self):
        review = self.create_review(3)

        found_review = models.Review.query.get(review.id)
        self.assertEqual(found_review.rating, 3)
        self.assertEqual(found_review.work.id, review.work.id)

        found_review.rating = 4
        self.db.session.commit()

        found_again_review = models.Review.query.get(review.id)
        self.assertEqual(found_review.rating, 4)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            review = self.create_review('foo')
        with self.assertRaises(ValueError):
            review = self.create_review(-1)
        with self.assertRaises(ValueError):
            review = self.create_review(6)

