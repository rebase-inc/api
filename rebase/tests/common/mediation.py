from math import floor

from rebase import models
from rebase.common import mock
from rebase.common.state import ManagedState
from rebase.tests.common.use_case import UseCase

class MediationUseCase(UseCase):

    def base_scenario(self, db):
        managed_state = ManagedState()
        ticket = mock.create_one_github_ticket(db)
        contractor = mock.create_one_contractor(db)
        user_1 = ticket.project.organization.managers[0].user
        user_2 = contractor.user
        auction = mock.create_one_auction(db, [ticket])
        auction.state = 'ended'
        snapshot = ticket.snapshots[0]
        nomination = mock.create_one_nomination(db, auction, contractor, approved=True)
        work_offer = models.WorkOffer(contractor, snapshot, floor(0.8*auction.ticket_set.bid_limits[0].price))
        bid = models.Bid(auction, contractor, [work_offer])
        contract = models.Contract(bid)
        work = work_offer.work
        # need to commit now to set the default state of the work
        db.session.commit()
        with managed_state:
            work.machine.send('halt_work', 'Just because...')
            work.machine.send('resume_work')
            work.machine.send('review')
            work.machine.send('mediate')

        mediation_1 = work.mediation_rounds[0]

        # let's cross roles, the mgr will become the contractor of the contractor who is the mgr of his own project
        org_2 = mock.create_one_organization(db, user=user_2)
        project_2 = mock.create_one_project(db, organization=org_2)
        ticket_2 = mock.create_one_internal_ticket(db, project=project_2)
        auction_2 = mock.create_one_auction(db, [ticket_2])
        auction_2.state = 'ended'
        contractor_2 = mock.create_one_contractor(db, user=user_1)
        nomination_2 = mock.create_one_nomination(db, auction_2, contractor_2, approved=True)
        snapshot_2 = ticket_2.snapshots[0]
        work_offer_2 = models.WorkOffer(contractor_2, snapshot_2, floor(0.8*auction_2.ticket_set.bid_limits[0].price))
        bid_2 = models.Bid(auction_2, contractor_2, [work_offer_2])
        contract_2 = models.Contract(bid_2)
        work_2 = work_offer_2.work
        # need to commit now to set the default state of the work
        db.session.commit()
        with managed_state:
            work_2.machine.send('halt_work', 'Just because...')
            work_2.machine.send('resume_work')
            work_2.machine.send('review')
            work_2.machine.send('mediate')

        mediation_2 = work_2.mediation_rounds[0]

        db.session.commit()
        return user_1, user_2, mediation_1, mediation_2
