import unittest

from . import RebaseModelTestCase
from rebase import models
from rebase.common import mock
from rebase.tests.common.organization import OrganizationUseCase

class TestOrganizationModel(RebaseModelTestCase):

    def test_joined_relationships(self):
        decoy_user = models.User('Foo', 'Bar', 'foobar@rebase.io', 'foobar')
        decoy_org = models.Organization('foobar', decoy_user)
        decoy_proj = models.Project(decoy_org, 'DECOOY')
        decoy_ticket = models.InternalTicket(decoy_proj, 'Decoy Ticket', 'Dont touch me')
        decoy_snap = models.TicketSnapshot(decoy_ticket)
        decoy_bid_limit = models.BidLimit(decoy_snap, 666)
        decoy_ticket_set = models.TicketSet([decoy_bid_limit])
        decoy_term_sheet = models.TermSheet('foobar')
        decoy_auction = models.Auction(decoy_ticket_set, decoy_term_sheet)

        user = models.User('Andrew', 'Millspaugh', 'andrew@rebase.io', 'foobar')
        organization = models.Organization('Rebase', user)
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
        self.assertEqual(set(reported_ticket_ids), set([first_ticket.id, second_ticket.id, third_ticket.id]))

        reported_snap_ids = []
        for snapshot in organization.ticket_snapshots:
            reported_snap_ids.append(snapshot.id)
            self.assertEqual(snapshot.organization, organization)
        self.assertEqual(set(reported_snap_ids), set([first_snap.id, second_snap.id, third_snap.id]))

        # test out the organization.bid_limits relationship
        reported_bid_limit_ids = []
        for bid_limit in organization.bid_limits:
            reported_bid_limit_ids.append(bid_limit.id)
            self.assertTrue(bid_limit.organization)
        self.assertEqual(set(reported_bid_limit_ids), set([first_bid_limit.id, second_bid_limit.id, third_bid_limit.id]))

        reported_ticket_set_ids = []
        for ticket_set in organization.ticket_sets:
            reported_ticket_set_ids.append(ticket_set.id)
            self.assertTrue(ticket_set.organization)
        self.assertEqual(set(reported_ticket_set_ids), set([first_ticket_set.id, second_ticket_set.id, third_ticket_set.id]))

        reported_auction_ids = []
        for auction in organization.auctions:
            reported_auction_ids.append(auction.id)
            self.assertTrue(auction.organization)
        self.assertEqual(set(reported_auction_ids), set([first_auction.id, second_auction.id, third_auction.id]))


class TestOrg(RebaseModelTestCase):

    def setUp(self):
        self.case = OrganizationUseCase(self.db)
        super().setUp()

    def test_contractor(self):
        validate_query_fn(
            self,
            Organization,
            self.case.user_2_as_contractor,
            Organization.as_contractor,
            'contractor',
            False, False, False, True
        )

    def test_mgr(self):
        validate_query_fn(
            self,
            Organization,
            self.case.user_1_as_mgr,
            Organization.as_manager,
            'manager',
            False, False, False, True
        )
