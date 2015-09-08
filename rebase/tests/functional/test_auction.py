import unittest
from datetime import datetime, timedelta
from functools import partialmethod
from math import floor

from . import PermissionTestCase, RebaseRestTestCase
from rebase.common import mock
from rebase.common.utils import ids, RebaseResource
from rebase.tests.common.auction import (
    case_contractor,
    case_mgr,
    case_admin,
    case_admin_collection,
    case_anonymous,
)


def _new_instance(auction):
    return {
        'duration':         auction.duration,
        'finish_work_by':   auction.finish_work_by.isoformat(),
        'ticket_set':       {
            'bid_limits': [ ids(bid_limit) for bid_limit in auction.ticket_set.bid_limits ]
        },
        'bids': [],
        'term_sheet':       ids(auction.term_sheet),
        'redundancy':       auction.redundancy,
    }

def _modify_this(auction):
    updated_auction = ids(auction)
    updated_auction.update({
        'duration': 2*auction.duration,
        'term_sheet': ids(auction.term_sheet),
        'redundancy': auction.redundancy
    })
    return updated_auction


class TestAuction(PermissionTestCase):
    model = 'Auction'
    _create = partialmethod(PermissionTestCase.create, new_instance=_new_instance)
    _modify = partialmethod(PermissionTestCase.modify, modify_this=_modify_this)

    def test_contractor_view(self):
        self.view(case_contractor, 'contractor', True)

    def _make_bid(self, user, auction, price_ratio):
        work_offers = []
        for bid_limit in auction.ticket_set.bid_limits:
            work_offer = {
                'ticket_snapshot': ids(bid_limit.ticket_snapshot),
                'price': floor(price_ratio*bid_limit.price),
                'contractor': ids(user.roles[0]),
            }
            work_offers.append(work_offer)

        bid = {
            'bid': {
                'auction' : ids(auction),
                'contractor' : ids(user.roles[0]),
                'work_offers' : work_offers
            }
        }
        return bid

    def test_contractor_over_bid(self):
        user, auction = self._run(case_contractor, 'contractor')

        over_bid = self._make_bid(user, auction, 1.2)
        auction_blob = self.post_resource('auctions/{}/bid_events'.format(auction.id), over_bid)['auction']
        self.assertEqual(auction_blob['state'], 'waiting_for_bids')

    def test_contractor_under_bid(self):
        user, auction = self._run(case_contractor, 'contractor')

        bid = self._make_bid(user, auction, 0.8)
        auction_blob = self.post_resource('auctions/{}/bid_events'.format(auction.id), bid)['auction']
        self.assertEqual(auction_blob['state'], 'ended')

    def test_fail_event(self):
        user, auction = self._run(case_admin, 'manager')

        auction_blob = self.post_resource('auctions/{}/fail_events'.format(auction.id), {})['auction']
        self.assertEqual(auction_blob['state'], 'failed')

    def test_contractor_collection(self):
        self.collection(case_contractor, 'contractor')

    def test_contractor_modify(self):
        self._modify(case_contractor, 'contractor', False)

    def test_contractor_delete(self):
        self.delete(case_contractor, 'contractor', False)

    def test_contractor_create(self):
        self._create(case_contractor, 'contractor', False)

    def test_mgr_collection(self):
        self.collection(case_mgr, 'manager')

    def _validate(self, auction_blob):
        self.assertIn('state', auction_blob)
        self.assertEqual(auction_blob['state'], 'created')

    def test_mgr_view(self):
        self.view(case_mgr, 'manager', True, validate=TestAuction._validate)

    def test_mgr_modify(self):
        self._modify(case_mgr, 'manager', True)

    def test_mgr_delete(self):
        self.delete(case_mgr, 'manager', True)

    def test_mgr_create(self):
        self._create(case_mgr, 'manager', True)

    def test_admin_view(self):
        self.view(case_admin, 'manager', True)

    def test_admin_modify(self):
        self._modify(case_admin, 'manager', True)

    def test_admin_delete(self):
        self.delete(case_admin, 'manager', True)

    def test_admin_create(self):
        self._create(case_admin, 'manager', True)

    def test_admin_collection(self):
        self.collection(case_admin_collection, 'manager')
