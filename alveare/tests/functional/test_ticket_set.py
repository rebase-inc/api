from unittest import skip
from copy import copy

from . import AlveareRestTestCase, AlveareNoMockRestTestCase
from alveare.common.utils import AlveareResource, validate_resource_collection
from alveare.tests.common.ticket_set import (
    case_contractor,
    case_mgr,
    case_admin,
    case_anonymous,
)

class TestTicketSetResource(AlveareRestTestCase):
    def setUp(self):
        self.resource = AlveareResource(self, 'TicketSet')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        ticket_set = self.resource.get_any()
        self.assertTrue(ticket_set)
        self.assertTrue(ticket_set['id'])
        self.assertIsInstance(ticket_set['auction']['id'], int)
        self.assertIsInstance(ticket_set['bid_limits'], list)

    @skip('ticket set doesnt have any updatable fields')
    def test_update(self):
        self.login_admin()
        pass

    def test_delete(self):
        self.login_admin()
        self.resource.delete_any()

    def test_delete_auction(self):
        self.login_admin()
        ticket_set = self.resource.get_any()
        self.delete_resource('auctions/{id}'.format(**ticket_set['auction']))
        self.get_resource(self.resource.url(ticket_set), 404)

class TestTicketSet(AlveareNoMockRestTestCase):
    def setUp(self):
        self.resource = AlveareResource(self, 'TicketSet')
        super().setUp()

    def _run(self, case):
        user, ticket_set = case(self.db)
        self.login(user.email, 'foo')
        return user, ticket_set

    def _test_ticket_set_collection(self, case):
        user, ticket_set = self._run(case)
        validate_resource_collection(self, user, [ticket_set] if ticket_set else [])

    def _test_ticket_set_view(self, case, view):
        _, ticket_set = self._run(case)
        ticket_set_blob = self.resource.get(ticket_set.id, 200 if view else 401)

    def _test_ticket_set_modify(self, case, modify):
        _, ticket_set = self._run(case)
        new_ticket_set_blob = {
            'id': ticket_set.id,
        }
        self.resource.update(expected_status=200 if modify else 401, **new_ticket_set_blob)

    def _test_ticket_set_delete(self, case, delete):
        _, ticket_set = self._run(case)
        ticket_set_blob = {
            'id': ticket_set.id
        }
        self.resource.delete(expected_status=200 if delete else 401, **ticket_set_blob)

    def _test_ticket_set_create(self, case, create):
        user, ticket_set = self._run(case)
        bid_limit = ticket_set.bid_limits[0]
        new_ticket_set_blob = {
            'bid_limits': [
                {
                    'id': bid_limit.id,
                    'price': bid_limit.price,
                    'ticket_snapshot': {'id': bid_limit.ticket_snapshot.id}
                }
            ]
        }
                 
        self.resource.create(expected_status=201 if create else 401, **new_ticket_set_blob)

    def test_mgr_collection(self):
        self._test_ticket_set_collection(case_mgr)

    def test_mgr_view(self):
        self._test_ticket_set_view(case_mgr, True)

    def test_mgr_modify(self):
        self._test_ticket_set_modify(case_mgr, True)

    def test_mgr_delete(self):
        self._test_ticket_set_delete(case_mgr, True)

    def test_mgr_create(self):
        self._test_ticket_set_create(case_mgr, True)

    def test_contractor_collection(self):
        self._test_ticket_set_collection(case_contractor)

    def test_contractor_view(self):
        self._test_ticket_set_view(case_contractor, True)

    def test_contractor_modify(self):
        self._test_ticket_set_modify(case_contractor, False)

    def test_contractor_delete(self):
        self._test_ticket_set_delete(case_contractor, False)

    def test_contractor_create(self):
        self._test_ticket_set_create(case_contractor, False)
