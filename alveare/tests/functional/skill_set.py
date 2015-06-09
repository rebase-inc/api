from copy import copy

from . import AlveareRestTestCase, AlveareNoMockRestTestCase
from alveare.common.mock import create_one_user
from alveare.tests.common.comment import (
    case_mgr,
    case_contractor,
)
from alveare.common.utils import AlveareResource, validate_resource_collection

class TestComment(AlveareNoMockRestTestCase):
    def setUp(self):
        super().setUp()
        self.resource =             AlveareResource(self, 'Comment')
        self.ticket_resource =      AlveareResource(self, 'Ticket')
        self.mediation_resource =   AlveareResource(self, 'Mediation')
        self.review_resource =      AlveareResource(self, 'Review')
        self.feedback_resource =    AlveareResource(self, 'Feedback')
        
    def _test_comment(self, case, resource, parent):
        user, comment = case(self.db)
        validate_resource_collection(self, user, [comment])
        comment_blob = self.resource.get(comment.id)
        self.resource.update(**comment_blob)
        self.resource.delete(**comment_blob)
        new_comment_blob = copy(comment_blob)
        del new_comment_blob['id']
        self.resource.create(**new_comment_blob)
        
        # negative tests
        user, comment = case(self.db)
        other_user = create_one_user(self.db)
        self.login(other_user.email, 'foo')
        self.resource.get(comment.id, 401)
        self.resource.update(expected_status=401, **comment_blob)
        self.resource.delete(expected_status=401, **comment_blob)
        self.resource.create(expected_status=401, **new_comment_blob)

        # admin tests
        self.login_admin()
        comment_blob = self.resource.get(comment.id)
        self.resource.update(**comment_blob)
        self.resource.delete(**comment_blob)
        new_comment_blob = copy(comment_blob)
        del new_comment_blob['id']
        self.resource.create(**new_comment_blob)

    def test_mgr_ticket_comment(self):
        self._test_comment(case_mgr_ticket_comment, self.ticket_resource, 'ticket')

    def test_contractor_ticket_comment(self):
        self._test_comment(case_contractor_ticket_comment, self.ticket_resource, 'ticket')

    def test_mgr_mediation_comment(self):
        self._test_comment(case_mgr_mediation_comment, self.mediation_resource, 'mediation')

    def test_contractor_mediation_comment(self):
        self._test_comment(case_contractor_mediation_comment, self.mediation_resource, 'mediation')

    def test_mgr_review_comment(self):
        self._test_comment(case_mgr_review_comment, self.review_resource, 'review')

    def test_contractor_review_comment(self):
        self._test_comment(case_contractor_review_comment, self.review_resource, 'review')

    def test_mgr_feedback_comment(self):
        self._test_comment(case_mgr_feedback_comment, self.feedback_resource, 'feedback')

    def test_contractor_feedback_comment(self):
        self._test_comment(case_contractor_feedback_comment, self.feedback_resource, 'feedback')
