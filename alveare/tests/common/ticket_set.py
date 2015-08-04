from rebase import models
from rebase.common import mock
from rebase.common.utils import pick_an_organization_name

def base_scenario(db):
    mgr_user = mock.create_one_user(db)
    org = mock.create_one_organization(db, pick_an_organization_name(), mgr_user)
    project = mock.create_one_github_project(db, org, 'Snapy Project')
    ticket = mock.create_one_github_ticket(db, 123, project)
    contractor = mock.create_one_contractor(db)
    auction = mock.create_one_auction(db, [ticket])
    snapshot = ticket.snapshots[0]
    nomination = mock.create_one_nomination(db, auction, contractor, approved=True)
    db.session.commit()
    return mgr_user, contractor, auction.ticket_set

def case_contractor(db):
    _, contractor, ticket_set = base_scenario(db)
    return contractor.user, ticket_set

def case_mgr(db):
    mgr_user, _, ticket_set = base_scenario(db)
    return mgr_user, ticket_set

def case_admin(db):
    _, _, ticket_set = base_scenario(db)
    admin_user = mock.create_one_user(db)
    admin_user.admin = True
    db.session.commit()
    return admin_user, ticket_set

def case_anonymous(db):
    _, _, _ = base_scenario(db)
    anonymous_user = mock.create_one_user(db)
    db.session.commit()
    return anonymous_user, None
