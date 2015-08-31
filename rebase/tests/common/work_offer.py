from math import floor

from rebase import models
from rebase.common import mock
from rebase.common.utils import pick_an_organization_name

def base_scenario(db):
    mgr_user = mock.create_one_user(db)
    org = mock.create_one_organization(db, pick_an_organization_name(), mgr_user)
    project = mock.create_one_github_project(db, org, 'Biddleton Project')
    ticket_1 = mock.create_one_github_ticket(db, 123, project)
    ticket_2 = mock.create_one_github_ticket(db, 123, project)
    contractor = mock.create_one_contractor(db)
    auction = mock.create_one_auction(db, [ticket_1, ticket_2])
    snapshot_1 = ticket_1.snapshots[0]
    snapshot_2 = ticket_2.snapshots[0]
    work_offer = models.WorkOffer(contractor, snapshot_1, floor(0.8*auction.ticket_set.bid_limits[0].price))
    bid = models.Bid(auction, contractor, [work_offer])
    db.session.add(bid)
    db.session.commit()
    return mgr_user, contractor, work_offer, snapshot_2

def case_contractor(db):
    # first duplicate the data to verify the queries discriminate between users properly
    base_scenario(db) 
    _, contractor, work_offer, _ = base_scenario(db)
    return contractor.user, work_offer

def case_mgr(db):
    # first duplicate the data to verify the queries discriminate between users properly
    base_scenario(db) 
    mgr_user, _, work_offer, _ = base_scenario(db)
    return mgr_user, work_offer

def case_mgr_collection(db):
    # first duplicate the data to verify the queries discriminate between users properly
    base_scenario(db) 
    mgr_user, _, work_offer, _ = base_scenario(db)
    return mgr_user, work_offer

def case_mgr_create(db):
    # first duplicate the data to verify the queries discriminate between users properly
    base_scenario(db) 
    mgr_user, _, work_offer, snapshot_2 = base_scenario(db)
    return mgr_user, work_offer, snapshot_2

def case_admin(db):
    admin_user = mock.create_one_user(db)
    admin_user.admin = True
    db.session.commit()
    return admin_user, work_offers[0]
