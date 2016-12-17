from sqlalchemy.exc import InterfaceError
from sqlalchemy.orm.exc import ObjectDeletedError

from . import RebaseModelTestCase
from rebase import models
from rebase.common import mock
from rebase.common.utils import validate_query_fn
from rebase.tests.common.comment import (
    case_mgr_ticket_comment,
    case_contractor_ticket_comment,
    case_mgr_mediation_comment,
    case_contractor_mediation_comment,
    case_mgr_review_comment,
    case_contractor_review_comment,
    case_mgr_feedback_comment,
    case_contractor_feedback_comment,
)

class TestCommentModel(RebaseModelTestCase):

    def test_create(self):
        review = mock.create_one_work_review(self.db, mock.create_one_user(self.db), 4, 'Hello')
        self.db.session.commit()

        self.assertEqual(review.comments.one().content, 'Hello')
        self.db.session.commit()

    def test_delete(self):
        review = mock.create_one_work_review(self.db,mock.create_one_user(self.db), 4, 'Bye')
        self.db.session.commit()

        self.delete_instance(review.comments.one())
        self.assertNotEqual(models.Review.query.get(review.id), None)

    def test_update(self):
        comment = mock.create_one_work_review(self.db, mock.create_one_user(self.db), 4, 'Foo').comments.one()
        self.db.session.commit()

        comment.content = 'Bar'
        self.db.session.commit()

        modified_comment = models.Comment.query.get(comment.id)
        self.assertEqual(modified_comment.content, 'Bar')

    def test_ticket_comment_as_manager(self):
        validate_query_fn(
            self,
            models.Comment,
            case_mgr_ticket_comment,
            models.Comment.as_manager,
            'manager',
            True, True, True, True
        )

    def test_ticket_comment_as_contractor(self):
        validate_query_fn(
            self,
            models.Comment,
            case_contractor_ticket_comment,
            models.Comment.as_contractor,
            'contractor',
            True, True, True, True
        )

    def test_ticket_comment_as_user(self):
        _, comment = case_contractor_ticket_comment(self.db)
        unrelated_user = mock.create_one_user(self.db)
        unrelated_user.set_role('manager')
        self.assertFalse(comment.allowed_to_be_created_by(unrelated_user))
        self.assertFalse(comment.allowed_to_be_modified_by(unrelated_user))
        self.assertFalse(comment.allowed_to_be_deleted_by(unrelated_user))

    def test_mediation_comment_as_manager(self):
        validate_query_fn(
            self,
            models.Comment,
            case_mgr_mediation_comment,
            models.Comment.as_manager,
            'manager',
            True, True, True, True
        )

    def test_mediation_comment_as_contractor(self):
        validate_query_fn(
            self,
            models.Comment,
            case_contractor_mediation_comment,
            models.Comment.as_contractor,
            'contractor',
            True, True, True, True
        )

    def test_mediation_comment_as_user(self):
        _, comment = case_contractor_mediation_comment(self.db)
        unrelated_user = mock.create_one_user(self.db)
        unrelated_user.set_role('contractor')
        self.assertFalse(comment.allowed_to_be_created_by(unrelated_user))
        self.assertFalse(comment.allowed_to_be_modified_by(unrelated_user))
        self.assertFalse(comment.allowed_to_be_deleted_by(unrelated_user))

    def test_review_comment_as_manager(self):
        validate_query_fn(
            self,
            models.Comment,
            case_mgr_review_comment,
            models.Comment.as_manager,
            'manager',
            True, True, True, True
        )

    def test_review_comment_as_contractor(self):
        validate_query_fn(
            self,
            models.Comment,
            case_contractor_review_comment,
            models.Comment.as_contractor,
            'contractor',
            True, True, True, True
        )

    def test_review_comment_as_user(self):
        _, comment = case_contractor_review_comment(self.db)
        unrelated_user = mock.create_one_user(self.db)
        unrelated_user.set_role('manager')
        self.assertFalse(comment.allowed_to_be_created_by(unrelated_user))
        self.assertFalse(comment.allowed_to_be_modified_by(unrelated_user))
        self.assertFalse(comment.allowed_to_be_deleted_by(unrelated_user))

    def test_feedback_comment_as_manager(self):
        validate_query_fn(
            self,
            models.Comment,
            case_mgr_feedback_comment,
            models.Comment.as_manager,
            'manager',
            False, False, False, True
        )

    def test_feedback_comment_as_contractor(self):
        validate_query_fn(
            self,
            models.Comment,
            case_contractor_feedback_comment,
            models.Comment.as_contractor,
            'contractor',
            True, True, True, True
        )

    def test_feedback_comment_as_user(self):
        _, comment = case_contractor_feedback_comment(self.db)
        unrelated_user = mock.create_one_user(self.db)
        self.assertFalse(comment.allowed_to_be_created_by(unrelated_user))
        self.assertFalse(comment.allowed_to_be_modified_by(unrelated_user))
        self.assertFalse(comment.allowed_to_be_deleted_by(unrelated_user))
