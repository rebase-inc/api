from unittest import skip

from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from alveare.models.nomination import Nomination

class TestNominationResource(AlveareRestTestCase):
    def setUp(self):
        self.nomination_resource = AlveareResource(self, 'Nomination')
        self.contractor_resource = AlveareResource(self, 'Contractor')
        self.ticket_set_resource = AlveareResource(self, 'TicketSet')
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

        self.post_resource('auth', dict(user={'id': user.id}, password= 'foo'))
        self.put_resource('nominations/{}/{}'.format(nomination.contractor_id, nomination.ticket_set_id), dict(auction={'id': auction_id}))

        nomination = self.get_resource('nominations/{}/{}'.format(nomination.contractor_id, nomination.ticket_set_id))['nomination']
        self.assertEqual(nomination['auction']['id'], auction_id)

    def test_delete(self):
        self.login_admin()
        self.nomination_resource.delete_any()

    def test_delete_contractor(self):
        self.login_admin()
        nomination = self.nomination_resource.get_any()
        self.contractor_resource.delete(nomination['contractor'])
        self.nomination_resource.get(nomination, 404)

    def test_delete_ticket_set(self):
        self.login_admin()
        nomination = self.nomination_resource.get_any()
        self.ticket_set_resource.delete(nomination['ticket_set'])
        self.nomination_resource.get(nomination, 404)

    def test_delete_organization(self):
        self.login_admin()
        nomination = self.nomination_resource.get_any()
        ticket_set = self.ticket_set_resource.get(nomination['ticket_set'])
        bid_limit =         AlveareResource(self, 'BidLimit').get(ticket_set['bid_limits'][0])
        ticket_snapshot =   AlveareResource(self, 'TicketSnapshot').get(bid_limit['ticket_snapshot'])
        ticket =            AlveareResource(self, 'Ticket').get(ticket_snapshot['ticket'])
        project =           AlveareResource(self, 'Project').get(ticket['project'])
        org_resource =      AlveareResource(self, 'Organization')

        organization = org_resource.get(project['organization'])
        org_resource.delete(organization)
        self.nomination_resource.get(nomination, 404)

    def test_that_new_user_cant_see_any_nominations(self):
        self.login_admin()
        self.logout()
        self.login_as_new_user()

        from alveare.models.nomination import Nomination
        nomination = Nomination.query.first()
        self.get_resource('nominations/{}/{}'.format(nomination.contractor_id, nomination.ticket_set_id), 401)

        nominations = self.get_resource('nominations')['nominations']
        self.assertEqual(nominations, [])

        user = nomination.ticket_set.bid_limits[0].ticket_snapshot.ticket.project.organization.managers[0].user

        self.logout()
        self.post_resource('auth', dict(user={'id': user.id}, password='foo'))
        nominations = self.get_resource('nominations')['nominations']
        #nomination_ids = [nom['id'] for nom in nominations]
        nominations = [(nom['contractor']['id'], nom['ticket_set']['id']) for nom in nominations]
        nomination = (nomination.contractor_id, nomination.ticket_set_id)
        self.assertIn(nomination, nominations)


