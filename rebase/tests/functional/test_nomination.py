from copy import copy
from math import floor

from . import PermissionTestCase
from rebase.common.database import ids
from rebase.tests.common.nomination import (
    case_contractor,
    case_mgr,
    case_admin,
    case_admin_collection,
    case_anonymous,
)


class TestNomination(PermissionTestCase):
    model = 'Nomination'

    def new(_, nomination):
        return {
            'contractor':         nomination.contractor,
            'ticket_set':       {
                'bid_limits': [ ids(bid_limit) for bid_limit in nomination.ticket_set.bid_limits ]
            },
            'auction':       nomination.auction,
        }

    def update(self, nomination):
        updated_nomination = ids(nomination)
        updated_nomination.update({
        })
        return updated_nomination

    def validate_view(self, nomination):
        self.assertTrue(nomination)
        fields = [
            'contractor_id',
            'ticket_set_id',
            'contractor',
            'job_fit',
            'ticket_set',
            'auction'
        ]
        for field in fields:
            self.assertIn(field, nomination)

    def test_contractor_view(self):
        self.view(case_contractor, 'contractor', True)

    def test_contractor_collection(self):
        self.collection(case_contractor, 'contractor')

    def test_contractor_modify(self):
        self.modify(case_contractor, 'contractor', False)

    def test_contractor_delete(self):
        self.delete(case_contractor, 'contractor', False)

    def test_contractor_create(self):
        self.create(case_contractor, 'contractor', False)

    def test_mgr_collection(self):
        self.collection(case_mgr, 'manager')

    def test_mgr_view(self):
        self.view(case_mgr, 'manager', True)

    def test_mgr_modify(self):
        self.modify(case_mgr, 'manager', True)

    def test_mgr_delete(self):
        self.delete(case_mgr, 'manager', True)

    def test_mgr_create(self):
        self.create(case_mgr, 'manager', True)

    def test_admin_view(self):
        self.view(case_admin, 'manager', True)

    def test_admin_modify(self):
        self.modify(case_admin, 'manager', True)

    def test_admin_delete(self):
        self.delete(case_admin, 'manager', True)

    def test_admin_create(self):
        self.create(case_admin, 'manager', True)

    def test_admin_collection(self):
        self.collection(case_admin_collection, 'manager')
