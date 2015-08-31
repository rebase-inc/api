import unittest
from datetime import datetime, timedelta
from functools import partial
from math import floor

from . import PermissionTestCase, RebaseRestTestCase
from rebase.common import mock
from rebase.common.utils import ids, RebaseResource
from rebase.tests.common.auction import (
    case_contractor,
    case_mgr,
    case_admin,
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
    _create = partial(PermissionTestCase._create, new_instance=_new_instance)
    _modify = partial(PermissionTestCase._modify, modify_this=_modify_this)

    def test_contractor_view(self):
        self._view(case_contractor, True)

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

    def _delete_all_my_bids(self, user):
        bid_resource =  RebaseResource(self, 'Bid')
        bids = bid_resource.get_all()
        for bid in bids:
            bid_resource.delete(**bid)

    def test_contractor_over_bid(self):
        user, auction = self._run(case_contractor)

        over_bid = self._make_bid(user, auction, 1.2)
        auction_blob = self.post_resource('auctions/{}/bid_events'.format(auction.id), over_bid)['auction']
        self.assertEqual(auction_blob['state'], 'waiting_for_bids')

    def test_contractor_under_bid(self):
        user, auction = self._run(case_contractor)

        bid = self._make_bid(user, auction, 0.8)
        auction_blob = self.post_resource('auctions/{}/bid_events'.format(auction.id), bid)['auction']
        self.assertEqual(auction_blob['state'], 'ended')

    def test_contractor_modify(self):
        TestAuction._modify(self, case_contractor, False)

    def test_contractor_delete(self):
        self._delete(case_contractor, False)

    def test_contractor_create(self):
        TestAuction._create(self, case_contractor, False)

    def test_mgr_view(self):
        self._view(case_mgr, True)

    def test_mgr_modify(self):
        TestAuction._modify(self, case_mgr, True)

    def test_mgr_delete(self):
        self._delete(case_mgr, True)

    def test_mgr_create(self):
        TestAuction._create(self, case_mgr, True)

class TestAuctionResource(RebaseRestTestCase):
    def setUp(self):
        self.contractor_resource =  RebaseResource(self, 'Contractor')
        self.user_resource =        RebaseResource(self, 'User')
        super().setUp()

    def test_get_auctions_for_org_and_by_approval(self):
        self.get_resource('auctions', 401)
        user_data = dict(
            first_name = 'Andrew',
            last_name = 'Millspaugh',
            email = 'andrew@auction.rebase.io',
            password = 'foobar'
        )
        user = self.post_resource('users', user_data)['user']
        self.post_resource('auth', dict(user=user, password='foobar')) #login

        self.logout()
        foo = self.login(user_data['email'], user_data['password'])

        org_data = dict(name='Bitstrap', user=user)
        organization = self.post_resource('organizations', org_data)['organization']

        project_data = dict(organization=organization, name='Some stupid app')
        project = self.post_resource('projects', project_data)['project']

        ticket_data = dict(project=project, title='TiTlE', description='dEsCrIpTiOn')
        ticket = self.post_resource('internal_tickets', ticket_data)['internal_ticket']

        ticket_snapshot = self.post_resource('ticket_snapshots', dict(ticket=ticket))['ticket_snapshot']
        bid_limit = self.post_resource('bid_limits', dict(ticket_snapshot=ticket_snapshot, price=999))['bid_limit']

        ticket_set = self.post_resource('ticket_sets', dict(bid_limits=[bid_limit]))['ticket_set']
        term_sheet = self.get_resource('term_sheets')['term_sheets'][0]
        auction_data = dict(
            ticket_set = ticket_set,
            finish_work_by = '2015-03-20T01:58:51.593347+00:00',
            duration = 123423, # no clue what this number means
            redundancy = 1,
            term_sheet = term_sheet
        )
        auction = self.post_resource('auctions', auction_data)['auction']
        auctions = self.get_resource('auctions')['auctions']
        self.assertEqual(len(auctions), 1)
        self.assertEqual(auctions, [auction])

        managers = self.get_resource('organizations/{id}'.format(**organization))['organization']['managers']
        users_who_are_managers = [manager['user'] for manager in managers]

        all_users = self.get_resource('users')['users']
        users_that_arent_manager = filter(lambda user: user['id'] not in users_who_are_managers, all_users)
        users_that_are_contractors = filter(lambda user: 'contractor' in [role['type'] for role in user['roles']], users_that_arent_manager)
        users_that_arent_admin = filter(lambda user: not user['admin'], users_that_are_contractors)
        new_contractor = mock.create_one_contractor(self.db)
        self.db.session.commit()
        our_user = self.user_resource.get(new_contractor.user.id)
        our_contractor = self.contractor_resource.get(new_contractor.id)

        auction_nominations = auction['ticket_set']['nominations']
        self.assertEqual(auction_nominations, [])

        nomination = self.post_resource('nominations', dict(ticket_set=auction['ticket_set'], contractor=our_contractor))['nomination']
        contractor_id = nomination['contractor']['id']
        ticket_set_id = nomination['ticket_set']['id']

        self.post_resource('auth', dict(user=our_user, password='foo')) #login

        our_users_auctions = self.get_resource('auctions')['auctions']
        self.assertNotIn(auction['id'], [a['id'] for a in our_users_auctions])

        self.post_resource('auth', dict(user=user, password='foobar')) #login
        self.put_resource('nominations/{}/{}'.format(contractor_id, ticket_set_id), dict(auction=auction))
        our_users_auctions = self.get_resource('auctions')['auctions']
        self.assertIn(auction['id'], [a['id'] for a in our_users_auctions])

    def test_get_all(self):
        self.login_admin()
        response = self.get_resource('auctions')
        self.assertIn('auctions', response)
        self.assertIsInstance(response['auctions'], list)

    def test_get_one(self):
        self.login_admin()
        response = self.get_resource('auctions')
        auction_id = response['auctions'][0]['id']

        response = self.get_resource('auctions/{}'.format(auction_id))
        auction = response['auction']

        self.assertEqual(auction.pop('id'), auction_id)
        self.assertIsInstance(auction.pop('ticket_set'), dict)
        self.assertIsInstance(auction.pop('duration'), int)
        self.assertIsInstance(auction.pop('finish_work_by'), str)
        self.assertIsInstance(auction.pop('redundancy'), int)
        self.assertIsInstance(auction.pop('term_sheet'), dict)
        self.assertIsInstance(auction.pop('bids'), list)

    def test_create_new(self):
        self.login_admin()
        ticket = self.get_resource('tickets')['tickets'][0]
        project = self.get_resource('projects/{id}'.format(**ticket['project']))['project']
        ticket_snapshot = self.post_resource('ticket_snapshots', dict(ticket=ticket))['ticket_snapshot']
        bid_limit = self.post_resource('bid_limits', dict(ticket_snapshot=ticket_snapshot, price=1000))['bid_limit']
        auction_data = dict(
            organization = project['organization'],
            ticket_set = dict(bid_limits=[bid_limit]),
            term_sheet = dict(legalese='Thou shalt not steal'),
            redundancy = 2
        )

        auction = self.post_resource('auctions', auction_data)['auction']

        self.assertIsInstance(auction.pop('id'), int)
        self.assertEqual(auction.pop('bids'), [])
        self.assertIsInstance(auction.pop('duration'), int)
        self.assertIsInstance(auction.pop('finish_work_by'), str)
        self.assertEqual(auction.pop('state'), 'created')
        self.assertEqual(auction.pop('redundancy'), 2)

        ticket_set = auction.pop('ticket_set')
        self.assertIsInstance(ticket_set.pop('id'), int)

        bid_limits = ticket_set.pop('bid_limits')
        bid_limit = bid_limits.pop()
        self.assertEqual(bid_limits, [])
        self.assertIsInstance(bid_limit.pop('id'), int)
        self.assertEqual(bid_limit.pop('price'), 1000)

        ticket_snapshot = bid_limit.pop('ticket_snapshot')
        self.assertEqual(bid_limit, {})
        self.assertIsInstance(ticket_snapshot.pop('id'), int)

        term_sheet = auction.pop('term_sheet')
        self.assertIsInstance(term_sheet.pop('id'), int)
        self.assertEqual(term_sheet.pop('legalese'), 'Thou shalt not steal')
        self.assertEqual(term_sheet, {})

        self.assertEqual(auction, {})

    def test_update(self):
        self.login_admin()
        auction = next(filter(lambda a: a['state'] == 'created', self.get_resource('auctions')['auctions']))

        auction = self.post_resource('auctions/{}/fail_events'.format(auction['id']), dict())['auction']
        self.assertEqual(auction.pop('state'), 'failed')

    def test_bid_on_auction(self):
        self.login_admin()
        auction = next(filter(lambda a: a['state'] == 'created', self.get_resource('auctions')['auctions']))
        contractor = self.get_resource('contractors')['contractors'][0]
        ticket_snapshot = { 'id' : auction['ticket_set']['bid_limits'][0]['ticket_snapshot']['id'] }
        work_offers = []
        for bid_limit in auction['ticket_set']['bid_limits']:
            work_offer = {
                'ticket_snapshot': bid_limit['ticket_snapshot'],
                'price': .8*bid_limit['price'],
                'contractor': contractor
            }
            work_offers.append(work_offer)

        bid = {
            'bid': {
                'auction' : { 'id': auction['id'] },
                'contractor' : { 'id': contractor['id'] },
                'work_offers' : work_offers
            }
        }
        auction = self.post_resource('auctions/{}/bid_events'.format(auction['id']), bid)['auction']
        self.assertEqual(auction.pop('state'), 'ended')
