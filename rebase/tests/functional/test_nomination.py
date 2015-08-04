from unittest import skip

from . import RebaseRestTestCase
from rebase.common.utils import RebaseResource
from rebase.models.nomination import Nomination

class TestNominationResource(RebaseRestTestCase):
    def setUp(self):
        self.nomination_resource = RebaseResource(self, 'Nomination')
        self.contractor_resource = RebaseResource(self, 'Contractor')
        self.ticket_set_resource = RebaseResource(self, 'TicketSet')
        super().setUp()

    def test_get_all(self):
        self.login_admin()
        nominations = self.nomination_resource.get_all()

    def test_get_one(self):
        self.login_admin()
        nomination = self.nomination_resource.get_any()
        self.assertTrue(nomination) # mock should have created at least one ticket and its related Nomination object
        self.assertTrue(self.contractor_resource.get(nomination['contractor']))
        self.assertTrue(self.ticket_set_resource.get(nomination['ticket_set']))

    def test_create(self):
        self.login_admin()
        self.nomination_resource.create(
            contractor = {'id': self.contractor_resource.get_any()['id']},
            ticket_set = {'id': self.ticket_set_resource.get_any()['id']},
        )

    def test_update(self):
        self.login_admin()
        self.logout()
        self.login_as_new_user()

        nomination = Nomination.query.first()
        auction_id = nomination.ticket_set.auction_id

        self.put_resource('nominations/{}/{}'.format(nomination.contractor_id, nomination.ticket_set_id), dict(auction={'id': auction_id}), 401)
        user = nomination.ticket_set.bid_limits[0].ticket_snapshot.ticket.project.organization.managers[0].user

        self.login(user.email, 'foo')
        self.put_resource('nominations/{}/{}'.format(nomination.contractor_id, nomination.ticket_set_id), dict(auction={'id': auction_id}))

        nomination = self.get_resource('nominations/{}/{}'.format(nomination.contractor_id, nomination.ticket_set_id))['nomination']
        self.assertEqual(nomination['auction']['id'], auction_id)

    def test_delete(self):
        self.login_admin()
        self.nomination_resource.delete_any()

    def test_delete_contractor(self):
        self.login_admin()
        nomination = self.nomination_resource.get_any()
        self.contractor_resource.delete(**nomination['contractor'])
        self.nomination_resource.get(nomination, 404)

    def test_delete_ticket_set(self):
        self.login_admin()
        nomination = self.nomination_resource.get_any()
        self.ticket_set_resource.delete(**nomination['ticket_set'])
        self.nomination_resource.get(nomination, 404)

    def test_delete_organization(self):
        self.login_admin()
        nomination = self.nomination_resource.get_any()
        ticket_set = self.ticket_set_resource.get(nomination['ticket_set'])
        bid_limit =         RebaseResource(self, 'BidLimit').get(ticket_set['bid_limits'][0])
        ticket_snapshot =   RebaseResource(self, 'TicketSnapshot').get(bid_limit['ticket_snapshot'])
        ticket =            RebaseResource(self, 'Ticket').get(ticket_snapshot['ticket'])
        project =           RebaseResource(self, 'Project').get(ticket['project'])
        org_resource =      RebaseResource(self, 'Organization')

        organization = org_resource.get(project['organization'])
        org_resource.delete(**organization)

        # testing all the way down because this seems to be a problem
        # fairly regularly
        self.get_resource('projects/{}'.format(project['id']), 404)
        self.get_resource('tickets/{}'.format(ticket['id']), 404)
        self.get_resource('ticket_snapshots/{}'.format(ticket_snapshot['id']), 404)
        self.get_resource('bid_limits/{}'.format(bid_limit['id']), 404)
        self.get_resource('ticket_sets/{}'.format(bid_limit['ticket_set']['id']), 404)
        self.get_resource('nominations/{contractor_id}/{ticket_set_id}'.format(**nomination), 404)

    def test_that_new_user_cant_see_any_nominations(self):
        self.login_admin()
        self.logout()
        self.login_as_new_user()

        from rebase.models.nomination import Nomination
        nomination = Nomination.query.first()
        self.get_resource('nominations/{}/{}'.format(nomination.contractor_id, nomination.ticket_set_id), 401)

        nominations = self.get_resource('nominations')['nominations']
        self.assertEqual(nominations, [])

        user = nomination.ticket_set.bid_limits[0].ticket_snapshot.ticket.project.organization.managers[0].user

        self.logout()
        self.login(user.email, 'foo')

        nominations = self.get_resource('nominations')['nominations']
        #nomination_ids = [nom['id'] for nom in nominations]
        nominations = [(nom['contractor']['id'], nom['ticket_set']['id']) for nom in nominations]
        nomination = (nomination.contractor_id, nomination.ticket_set_id)
        self.assertIn(nomination, nominations)


