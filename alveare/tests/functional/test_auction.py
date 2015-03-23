import unittest
from datetime import datetime, timedelta

from alveare.common import mock

from . import AlveareRestTestCase

class TestAuctionResource(AlveareRestTestCase):

    def test_get_auctions_for_org_and_by_approval(self):
        self.post_resource('auth', dict(), 401) #logout
        self.get_resource('auctions', 401)
        user_data = dict(
            first_name = 'Andrew',
            last_name = 'Millspaugh',
            email = 'andrew@alveare.io',
            password = 'foobar'
        )
        user = self.post_resource('users', user_data)['user']
        self.post_resource('auth', dict(user=user, password='foobar')) #login

        org_data = dict(name='Bitstrap', user=user)
        organization = self.post_resource('organizations', org_data)['organization']

        project_data = dict(organization=organization, name='Some stupid app')
        project = self.post_resource('projects', project_data)['project']

        ticket_data = dict(project=project, title='TiTlE', description='dEsCrIpTiOn')
        ticket = self.post_resource('internal_tickets', ticket_data)['internal_ticket']

        ticket_snapshot = self.post_resource('ticket_snapshots', dict(ticket=ticket))['ticket_snapshot']
        bid_limit = self.post_resource('bid_limits', dict(ticket_snapshot=ticket_snapshot, price=999))['bid_limit']

        ticket_set = self.post_resource('ticket_sets', dict(bid_limits=[bid_limit]))['ticket_set']
        term_sheet = self.post_resource('term_sheets', dict(legalese='piss off'))['term_sheet']
        auction_data = dict(
            organization = organization,
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
        our_user = next(users_that_arent_admin)
        our_contractor = next(filter(lambda role: role['type'] == 'contractor', our_user['roles']))

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
        response = self.get_resource('auctions')
        self.assertIn('auctions', response)
        self.assertIsInstance(response['auctions'], list)

    def test_get_one(self):
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
        self.assertEqual(ticket_snapshot, {})

        term_sheet = auction.pop('term_sheet')
        self.assertIsInstance(term_sheet.pop('id'), int)
        self.assertEqual(term_sheet.pop('legalese'), 'Thou shalt not steal')
        self.assertEqual(term_sheet, {})

        self.assertEqual(auction, {})

    def test_update(self):
        auction = next(filter(lambda a: a['state'] == 'created', self.get_resource('auctions')['auctions']))

        auction = self.post_resource('auctions/{}/fail_events'.format(auction['id']), dict())['auction']
        self.assertEqual(auction.pop('state'), 'failed')


