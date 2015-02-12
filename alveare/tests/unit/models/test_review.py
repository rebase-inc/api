from . import AlveareModelTestCase

from alveare import models

class TestReviewModel(AlveareModelTestCase):

    def test_create(self):
        work_offer = models.WorkOffer(100)
        work = self.create_model(models.Work, work_offer)
        review = self.create_model(models.Review, work, 1)
        _ = models.Comment(review, 'Hello')

        self.db.session.commit()
        found_review = models.Review.query.get(review.id)

        self.assertEqual(found_review.work.id, work.id)
        self.assertEqual(found_review.rating, 1)
        comment = found_review.comments.one()
        self.assertEqual(comment.content, 'Hello')

    def test_delete(self):
        work_offer = models.WorkOffer(100)
        work = self.create_model(models.Work, work_offer)
        review = self.create_model(models.Review, work, 2)

        found_review = models.Review.query.get(review.id)
        self.db.session.delete(found_review)
        self.db.session.commit()

        self.assertEqual(models.Review.query.get(review.id), None)

    def test_delete_comment(self):
        work = self.create_model(models.Work, models.WorkOffer(100))
        review = models.Review(work, 4)
        comment = self.create_model(models.Comment, review, 'Bye')
        self.delete_instance(models.Comment, comment)
        self.assertNotEqual(models.Review.query.get(review.id), None)

    def test_update(self):
        work_offer = models.WorkOffer(100)
        work = self.create_model(models.Work, work_offer)
        review = self.create_model(models.Review, work, 3)
        found_review = models.Review.query.get(review.id)
        self.assertEqual(found_review.rating, 3)
        self.assertEqual(found_review.work.id, work.id)

        found_review.rating = 4
        self.db.session.commit()

        found_again_review = models.Review.query.get(review.id)
        self.assertEqual(found_review.rating, 4)

    def test_bad_create(self):
        work_offer = models.WorkOffer(100)
        work = self.create_model(models.Work, work_offer)
        with self.assertRaises(ValueError):
            self.create_model(models.Review, work, 'foo')
        with self.assertRaises(ValueError):
            self.create_model(models.Review, work, -1)
        with self.assertRaises(ValueError):
            self.create_model(models.Review, work, 6)

