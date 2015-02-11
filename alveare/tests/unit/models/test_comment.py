from sqlalchemy.exc import InterfaceError

from . import AlveareModelTestCase

from alveare import models

class TestCommentModel(AlveareModelTestCase):
    model = models.Comment

    def test_create(self):
        work = self.create_model(models.Work, models.WorkOffer(100))
        review = models.Review(work, 4)
        new_comment = self.create_model(self.model, review, 'Hello')
        self.assertEqual(new_comment.content, 'Hello')

    def test_delete(self):
        work = self.create_model(models.Work, models.WorkOffer(100))
        review = models.Review(work, 4)
        new_comment = self.create_model(self.model, review, 'Bye')
        self.delete_instance(self.model, new_comment)

    def test_update(self):
        work = self.create_model(models.Work, models.WorkOffer(100))
        review = models.Review(work, 4)
        new_comment = self.create_model(self.model, review, 'Foo')
        self.assertEqual(new_comment.content, 'Foo')

        new_comment.content = 'Bar'
        self.db.session.commit()

        modified_comment = self.model.query.get(new_comment.id)
        self.assertEqual(modified_comment.content, 'Bar')

    def test_bad_create(self):
        work = self.create_model(models.Work, models.WorkOffer(100))
        review = models.Review(work, 4)
        with self.assertRaises(InterfaceError):
            self.create_model(self.model, review, str)

