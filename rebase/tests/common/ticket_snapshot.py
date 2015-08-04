from rebase import models
from rebase.common import mock
from rebase.common.utils import pick_an_organization_name

def case_as_manager(db):
    mgr_user = mock.create_one_user(db)
    org = mock.create_one_organization(db, pick_an_organization_name(), mgr_user)
    project = mock.create_one_github_project(db, org, 'Snapy Project')
    ticket = mock.create_one_github_ticket(db, 123, project)
    snapshot = mock.create_one_snapshot(db, ticket)
    db.session.commit()
    return mgr_user, snapshot

def case_past_work_as_contractor(db):
    mgr_user = mock.create_one_user(db)
    org = mock.create_one_organization(db, pick_an_organization_name(), mgr_user)
    project = mock.create_one_github_project(db, org, 'Snapy Project')
    ticket = mock.create_one_github_ticket(db, 123, project)
    snapshot = mock.create_one_snapshot(db, ticket)
    contractor = mock.create_one_contractor(db)
    other_contractor = mock.create_one_contractor(db)
    work_offer = mock.create_work_offer(db, contractor, snapshot, 1000)
    other_work_offer = mock.create_work_offer(db, other_contractor, snapshot, 1000)
    db.session.commit()
    return contractor.user, snapshot

def case_auctions_as_contractor(db):
    mgr_user = mock.create_one_user(db)
    org = mock.create_one_organization(db, pick_an_organization_name(), mgr_user)
    project = mock.create_one_github_project(db, org, 'Snapy Project')
    ticket = mock.create_one_github_ticket(db, 123, project)
    contractor = mock.create_one_contractor(db)
    auction = mock.create_one_auction(db, [ticket])
    snapshot = ticket.snapshots[0]
    nomination = mock.create_one_nomination(db, auction, contractor, approved=True)
    db.session.commit()
    return contractor.user, snapshot
