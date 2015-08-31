from math import floor

from rebase import models
from rebase.common import mock
from rebase.common.utils import pick_an_organization_name

def base_scenario(db):
    mgr_user = mock.create_one_user(db)
    org = mock.create_one_organization(db, pick_an_organization_name(), mgr_user)
    project = mock.create_one_github_project(db, org, 'Biddleton Project')
    ticket = mock.create_one_github_ticket(db, 123, project)
    contractor = mock.create_one_contractor(db)
    auction = mock.create_one_auction(db, [ticket])
    snapshot = ticket.snapshots[0]
    work_offer = models.WorkOffer(contractor, snapshot, floor(0.8*auction.ticket_set.bid_limits[0].price))
    bid = models.Bid(auction, contractor, [work_offer])
    nomination = mock.create_one_nomination(db, auction, contractor, approved=True)
    db.session.commit()
    return mgr_user, contractor, bid

def case_contractor(db):
    _, contractor, bid = base_scenario(db)
    return contractor.user, bid

def case_mgr(db):
    mgr_user, _, bid = base_scenario(db)
    return mgr_user, bid

def case_admin(db):
    _, _, bid = base_scenario(db)
    admin_user = mock.create_one_user(db)
    admin_user.admin = True
    db.session.commit()
    return admin_user, bid
