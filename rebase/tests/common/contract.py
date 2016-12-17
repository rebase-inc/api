from math import floor

from rebase import models
from rebase.common import mock
from rebase.common.utils import pick_an_organization_name

def base_scenario(db):
    ticket = mock.create_one_github_ticket(db)
    contractor = mock.create_one_contractor(db)
    user_1 = ticket.project.managers[0].user
    user_2 = contractor.user
    auction = mock.create_one_auction(db, [ticket])
    auction.state = 'ended'
    snapshot = ticket.snapshots[0]
    nomination = mock.create_one_nomination(db, auction, contractor, approved=True)
    work_offer = models.WorkOffer(contractor, snapshot, floor(0.8*auction.ticket_set.bid_limits[0].price))
    bid = models.Bid(auction, contractor, [work_offer])
    contract = models.Contract(bid)

    # let's cross roles, the mgr will become the contractor of the contractor who is the mgr of his own project
    org_2 = mock.create_one_organization(db, user=contractor.user)
    project_2 = mock.create_one_project(db, organization=org_2)
    ticket_2 = mock.create_one_internal_ticket(db, project=project_2)
    auction_2 = mock.create_one_auction(db, [ticket_2])
    auction_2.state = 'ended'
    contractor_2 = mock.create_one_contractor(db, user=user_1)
    nomination_2 = mock.create_one_nomination(db, auction_2, contractor_2, approved=True)
    snapshot_2 = ticket_2.snapshots[0]
    work_offer_2 = models.WorkOffer(contractor, snapshot_2, floor(0.8*auction_2.ticket_set.bid_limits[0].price))
    bid_2 = models.Bid(auction_2, contractor_2, [work_offer_2])
    contract_2 = models.Contract(bid_2)

    db.session.commit()
    return user_1, user_2, contract, contract_2

def case_user_2_as_contractor(db):
    _, user_2, contract, _ = base_scenario(db)
    return user_2, contract

def case_user_2_as_mgr(db):
    _, user_2, _, contract_2 = base_scenario(db)
    return user_2, contract_2

def case_user_1_as_mgr(db):
    user_1, _, contract, _ = base_scenario(db)
    return user_1, contract

def case_user_1_as_contractor(db):
    user_1, _, _, contract_2 = base_scenario(db)
    return user_1, contract_2

def case_admin_base(db):
    _, _, contract, contract_2 = base_scenario(db)
    admin_user = mock.create_one_user(db)
    admin_user.admin = True
    db.session.commit()
    return admin_user, contract, contract_2

def case_admin(db):
    admin_user, contract, _ = case_admin_base(db)
    return admin_user, contract

def case_admin_collection(db):
    admin_user, contract, contract_2 = case_admin_base(db)
    return admin_user, [contract, contract_2]
