import unittest

from . import AlveareModelTestCase
from alveare import models
from alveare.common import mock

class TestOrganizationModel(AlveareModelTestCase):

    def test_joined_relationships(self):
        decoy_user = models.User('Foo', 'Bar', 'foobar@alveare.io', 'foobar')
        decoy_org = models.Organization('foobar', decoy_user)
        decoy_proj = models.Project(decoy_org, 'DECOOY')
        decoy_ticket = models.InternalTicket(decoy_proj, 'Decoy Ticket', 'Dont touch me')
        decoy_snap = models.TicketSnapshot(decoy_ticket)
        decoy_bid_limit = models.BidLimit(decoy_snap, 666)
        decoy_ticket_set = models.TicketSet([decoy_bid_limit])
        decoy_term_sheet = models.TermSheet('foobar')
        decoy_auction = models.Auction(decoy_ticket_set, decoy_term_sheet)

        user = models.User('Andrew', 'Millspaugh', 'andrew@alveare.io', 'foobar')
        organization = models.Organization('Alveare', user)
        project = models.Project(organization, 'REST API')

        # make tickets
        first_ticket = models.InternalTicket(project, 'Some Ticket', 'Please do it')
        second_ticket = models.InternalTicket(project, 'Another Ticket', 'Please sir')
        third_ticket = models.InternalTicket(project, 'Last Ticket', 'I give up')

        # make snapshots
        first_snap = models.TicketSnapshot(first_ticket)
        second_snap = models.TicketSnapshot(second_ticket)
        third_snap = models.TicketSnapshot(third_ticket)

        # make bid limits
        first_bid_limit = models.BidLimit(first_snap, 100)
        second_bid_limit = models.BidLimit(second_snap, 200)
        third_bid_limit = models.BidLimit(third_snap, 300)

        # make ticket_sets
        first_ticket_set = models.TicketSet([first_bid_limit])
        second_ticket_set = models.TicketSet([second_bid_limit])
        third_ticket_set = models.TicketSet([third_bid_limit])

        term_sheet = models.TermSheet('foobarbaz')

        # make auctions
        first_auction = models.Auction(first_ticket_set, term_sheet)
        second_auction = models.Auction(second_ticket_set, term_sheet)
        third_auction = models.Auction(third_ticket_set, term_sheet)

        self.db.session.add(decoy_user)
        self.db.session.add(user)
        self.db.session.commit()

        # test out the organization.tickets relationship
        reported_ticket_ids = []
        for ticket in organization.tickets:
            reported_ticket_ids.append(ticket.id)
            self.assertEqual(ticket.organization, organization)
        self.assertEqual(reported_ticket_ids, [first_ticket.id, second_ticket.id, third_ticket.id])

        reported_snap_ids = []
        for snapshot in organization.ticket_snapshots:
            reported_snap_ids.append(snapshot.id)
            self.assertEqual(snapshot.organization, organization)
        self.assertEqual(reported_snap_ids, [first_snap.id, second_snap.id, third_snap.id])

        # test out the organization.bid_limits relationship
        reported_bid_limit_ids = []
        for bid_limit in organization.bid_limits:
            reported_bid_limit_ids.append(bid_limit.id)
            self.assertTrue(bid_limit.organization)
        self.assertEqual(reported_bid_limit_ids, [first_bid_limit.id, second_bid_limit.id, third_bid_limit.id])

        reported_ticket_set_ids = []
        for ticket_set in organization.ticket_sets:
            reported_ticket_set_ids.append(ticket_set.id)
            self.assertTrue(ticket_set.organization)
        self.assertEqual(reported_ticket_set_ids, [first_ticket_set.id, second_ticket_set.id, third_ticket_set.id])

        reported_auction_ids = []
        for auction in organization.auctions:
            reported_auction_ids.append(auction.id)
            self.assertTrue(auction.organization)
        self.assertEqual(reported_auction_ids, [first_auction.id, second_auction.id, third_auction.id])

    #@unittest.skip('Havent built this yet')
    #def test_create(self):
        #arbitration = mock.create_some_work(self.db).pop().mediation_rounds[0].arbitration
        #self.db.session.commit()

        #self.assertIsInstance(arbitration.mediation.work.offer.price, int)

    #@unittest.skip('Havent built this yet')
    #def test_delete(self):
        #arbitration = mock.create_some_work(self.db).pop().mediation_rounds[0].arbitration
        #self.db.session.commit()
        #self.delete_instance(arbitration)
        #self.assertEqual(models.Arbitration.query.get(arbitration.id), None)

    #@unittest.skip('Havent built this yet')
    #def test_update(self):
        #arbitration = self.create_arbitration()
        #self.db.session.commit()

        #arbitration.outcome = 4
        #self.db.session.commit()

        #modified_arbitration = models.Arbitration.query.get(arbitration.id)
        #self.assertEqual(modified_arbitration.outcome, 4)

    #@unittest.skip('Havent built this yet')
    #def test_bad_create(self):
        #with self.assertRaises(ValueError):
            #self.create_model(models.Arbitration, 'foo')
