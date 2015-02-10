from . import AlveareModelTestCase

from alveare import models

class TestReviewModel(AlveareModelTestCase):
    model = models.Review

    def test_create(self):
        work = self.create_model(models.Work)
        review = self.create_model(self.model, 3, work)
        found_review = self.model.query.get(review.id)

        self.assertEqual(found_review.work.id, work.id)
        self.assertEqual(found_review.rating, 3)

    def test_delete(self):
        work = self.create_model(models.Work)
        review = self.create_model(self.model, 3, work)

        found_review = self.model.query.get(review.id)
        self.db.session.delete(found_review)
        self.db.session.commit()

        self.assertEqual(self.model.query.get(review.id), None)

    def test_update(self):
        work = self.create_model(models.Work)
        review = self.create_model(self.model, 3, work)
        found_review = self.model.query.get(review.id)
        self.assertEqual(found_review.rating, 3)
        self.assertEqual(found_review.work.id, work.id)

        found_review.rating = 5
        self.db.session.commit()

        found_again_review = self.model.query.get(review.id)
        self.assertEqual(found_review.rating, 5)

    def test_bad_create(self):
        work = self.create_model(models.Work)
        with self.assertRaises(ValueError):
            self.create_model(self.model, 'foo', work)
        with self.assertRaises(ValueError):
            self.create_model(self.model, -1, work)
        with self.assertRaises(ValueError):
            self.create_model(self.model, 6, work)

