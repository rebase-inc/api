from sqlalchemy.exc import InterfaceError
from sqlalchemy.orm.exc import ObjectDeletedError

from . import AlveareModelTestCase

from alveare import models
from alveare.common import mock

class TestCommentModel(AlveareModelTestCase):

    def test_create(self):
        review = mock.create_one_work_review(self.db, 4, 'Hello')
        self.db.session.commit()

        self.assertEqual(review.comments.one().content, 'Hello')
        self.db.session.commit()

    def test_delete(self):
        review = mock.create_one_work_review(self.db, 4, 'Bye')
        self.db.session.commit()

        self.delete_instance(review.comments.one())
        self.assertNotEqual(models.Review.query.get(review.id), None)

    def test_update(self):
        comment = mock.create_one_work_review(self.db, 4, 'Foo').comments.one()
        self.db.session.commit()

        comment.content = 'Bar'
        self.db.session.commit()

        modified_comment = models.Comment.query.get(comment.id)
        self.assertEqual(modified_comment.content, 'Bar')

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            models.Review('foo', 'foo')
            self.db.session.commit()

