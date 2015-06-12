from copy import copy

from . import AlveareRestTestCase, AlveareNoMockRestTestCase
from alveare.common.mock import create_one_user
from alveare.tests.common.comment import (
    case_mgr_ticket_comment,
    case_contractor_ticket_comment,
    case_mgr_mediation_comment,
    case_contractor_mediation_comment,
    case_mgr_review_comment,
    case_contractor_review_comment,
    case_mgr_feedback_comment,
    case_contractor_feedback_comment,
)
from alveare.common.utils import AlveareResource, validate_resource_collection

class TestComment(AlveareNoMockRestTestCase):
    def setUp(self):
        super().setUp()
        self.resource =             AlveareResource(self, 'Comment')
        
    def _test_comment(self, case, create=True, modify=True, delete=True, view=True):
        user, comment = case(self.db)
        validate_resource_collection(self, user, [comment])
        if view:
            comment_blob = self.resource.get(comment.id)
        if modify:
            self.resource.update(**comment_blob)
        if delete:
            self.resource.delete(**comment_blob)
        if create and view:
            new_comment_blob = copy(comment_blob)
            del new_comment_blob['id']
            self.resource.create(**new_comment_blob)
        
        # negative tests
        user, comment = case(self.db)
        other_user = create_one_user(self.db)
        self.login(other_user.email, 'foo')
        self.resource.get(comment.id, 401)
        if view:
            self.resource.update(expected_status=401, **comment_blob)
            self.resource.delete(expected_status=401, **comment_blob)
        if create and view:
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
        self._test_comment(case_mgr_ticket_comment)

    def test_contractor_ticket_comment(self):
        self._test_comment(case_contractor_ticket_comment)

    def test_mgr_mediation_comment(self):
        self._test_comment(case_mgr_mediation_comment)

    def test_contractor_mediation_comment(self):
        self._test_comment(case_contractor_mediation_comment)

    def test_mgr_review_comment(self):
        self._test_comment(case_mgr_review_comment)

    def test_contractor_review_comment(self):
        self._test_comment(case_contractor_review_comment)

    def test_mgr_feedback_comment(self):
        self._test_comment(case_mgr_feedback_comment, False, False, False, True)

    def test_contractor_feedback_comment(self):
        self._test_comment(case_contractor_feedback_comment)
