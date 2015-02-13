from sqlalchemy.exc import InterfaceError
from sqlalchemy.orm.exc import ObjectDeletedError

from . import AlveareModelTestCase

from alveare import models

class TestCommentModel(AlveareModelTestCase):

    def test_create(self):
        review = self.create_review(4, 'Hello')
        self.assertEqual(review.comments.one().content, 'Hello')
        self.db.session.commit()

    def test_delete(self):
        review = self.create_review(4, 'Bye')
        self.delete_instance(review.comments.one())
        self.assertNotEqual(models.Review.query.get(review.id), None)

    def test_update(self):
        comment = self.create_review(4, 'Foo').comments.one()
        self.db.session.commit()

        comment.content = 'Bar'
        self.db.session.commit()

        modified_comment = models.Comment.query.get(comment.id)
        self.assertEqual(modified_comment.content, 'Bar')

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            comment = self.create_review('Foo', 'Foo').comments.one()
            self.db.session.commit()

