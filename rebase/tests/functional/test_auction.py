from copy import copy
from datetime import datetime, timedelta
from math import floor
from unittest import skip

from . import PermissionTestCase, RebaseRestTestCase
from rebase.common import mock
from rebase.common.database import ids
from rebase.common.utils import RebaseResource
from rebase.tests.common.auction import (
    case_contractor,
    case_mgr,
    case_admin,
    case_admin_collection,
    case_anonymous,
)



class TestAuction(PermissionTestCase):
    model = 'Auction'

    def new(_, auction):
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

    def update(self, auction):
        updated_auction = ids(auction)
        updated_auction.update({
            'duration': 2*auction.duration,
            'term_sheet': ids(auction.term_sheet),
            'redundancy': auction.redundancy
        })
        return updated_auction

    def validate_view(self, auction):
        self.assertTrue(auction)
        fields = [
            'id',
            'duration',
            'finish_work_by',
            'ticket_set',
            'bids',
            'term_sheet',
            'redundancy',
            'state',
            'approved_talents'
        ]
        for field in fields:
            self.assertIn(field, auction)
        self.assertEqual(auction['state'], 'created')

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

    def test_contractor_bid_on_invalid_auction(self):
        user, auction = self._run(case_contractor, 'contractor')

        bid = self._make_bid(user, auction, 0.8)
        self.post_resource(
            'auctions/{}/bid_events'.format(1000000000),
            bid,
            expected_code=404
        )

    def test_contractor_bad_bid_no_work_offers(self):
        user, auction = self._run(case_contractor, 'contractor')

        good_bid = self._make_bid(user, auction, 0.8)

        bad_bid = copy(good_bid)
        bad_bid['bid']['work_offers'].clear()
        self.post_resource(
            'auctions/{}/bid_events'.format(auction.id),
            bad_bid,
            expected_code=400
        )

    def test_contractor_bad_bid_wrong_snapshot(self):
        user, auction = self._run(case_contractor, 'contractor')

        good_bid = self._make_bid(user, auction, 0.8)

        bad_bid = copy(good_bid)
        bad_bid['bid']['work_offers'][0]['ticket_snapshot']['id'] = 99999999
        self.post_resource(
            'auctions/{}/bid_events'.format(auction.id),
            bad_bid,
            expected_code=404
        )

    def test_contractor_bad_bid_no_contractor(self):
        user, auction = self._run(case_contractor, 'contractor')

        good_bid = self._make_bid(user, auction, 0.8)

        bad_bid = copy(good_bid)
        del bad_bid['bid']['contractor']
        response = self.post_resource(
            'auctions/{}/bid_events'.format(auction.id),
            bad_bid,
            expected_code=400
        )
        print(response)

    def test_fail_event(self):
        user, auction = self._run(case_admin, 'manager')

        auction_blob = self.post_resource('auctions/{}/fail_events'.format(auction.id), {})['auction']
        self.assertEqual(auction_blob['state'], 'failed')

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

    def test_profile(self):
        from cProfile import Profile
        from pstats import Stats
        mock.DeveloperUserStory(self.db, 'Phil', 'Meyman', 'philmeyman@joinrebase.com', 'lem')
        mock.ManagerUserStory(self.db, 'Ron', 'Swanson', 'ron@joinrebase.com', 'ron')
        self.db.session.commit()
        self.login('ron@joinrebase.com', 'ron', 'manager')
        profile = Profile()
        profile.runcall(self.get_resource, '/auctions')
        stats = Stats(profile)
        stats.sort_stats('cumulative')
        stats.print_stats(.1, 'api\/rebase') # print first 10% and only show my code
        #import pdb; pdb.set_trace()
