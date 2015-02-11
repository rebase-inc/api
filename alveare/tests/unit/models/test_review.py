from . import AlveareModelTestCase

from alveare import models

class TestReviewModel(AlveareModelTestCase):
    model = models.Review

    def test_create(self):
        work_offer = models.WorkOffer(100)
        work = self.create_model(models.Work, work_offer)
        review = self.create_model(self.model, work, 1)
        _ = models.Comment(review, 'Hello')

        self.db.session.commit()
        found_review = self.model.query.get(review.id)

        self.assertEqual(found_review.work.id, work.id)
        self.assertEqual(found_review.rating, 1)
        comment = found_review.comments.one()
        self.assertEqual(comment.content, 'Hello')

    def test_delete(self):
        work_offer = models.WorkOffer(100)
        work = self.create_model(models.Work, work_offer)
        review = self.create_model(self.model, work, 2)

        found_review = self.model.query.get(review.id)
        self.db.session.delete(found_review)
        self.db.session.commit()

        self.assertEqual(self.model.query.get(review.id), None)

    def test_update(self):
        work_offer = models.WorkOffer(100)
        work = self.create_model(models.Work, work_offer)
        review = self.create_model(self.model, work, 3)
        found_review = self.model.query.get(review.id)
        self.assertEqual(found_review.rating, 3)
        self.assertEqual(found_review.work.id, work.id)

        found_review.rating = 4
        self.db.session.commit()

        found_again_review = self.model.query.get(review.id)
        self.assertEqual(found_review.rating, 4)

    def test_bad_create(self):
        work_offer = models.WorkOffer(100)
        work = self.create_model(models.Work, work_offer)
        with self.assertRaises(ValueError):
            self.create_model(self.model, work, 'foo')
        with self.assertRaises(ValueError):
            self.create_model(self.model, work, -1)
        with self.assertRaises(ValueError):
            self.create_model(self.model, work, 6)

