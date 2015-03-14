import unittest

from alveare.common import mock

from . import AlveareRestTestCase

class TestAuctionResource(AlveareRestTestCase):

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
        ticket_snapshot = self.post_resource('ticket_snapshots', dict(ticket=ticket))['ticket_snapshot']
        auction_data = dict(
            ticket_set = dict(bid_limits=[dict(ticket_snapshot=ticket_snapshot, price=1000)]),
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
        ticket = self.get_resource('tickets')['tickets'][0]
        ticket_snapshot = self.post_resource('ticket_snapshots', dict(ticket=ticket))['ticket_snapshot']
        auction_data = dict(
            ticket_set = dict(bid_limits=[dict(ticket_snapshot=ticket_snapshot, price=1000)]),
            term_sheet = dict(legalese='Thou shalt not steal'),
            redundancy = 2
        )

        auction = self.post_resource('auctions', auction_data)['auction']

        auction = self.post_resource('auctions/{}/fail_events'.format(auction['id']), dict())['auction']
        self.assertEqual(auction.pop('state'), 'failed')

