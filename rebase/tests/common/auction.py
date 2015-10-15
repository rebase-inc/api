from rebase import models
from rebase.common import mock

def base_scenario(db):
    ticket = mock.create_one_github_ticket(db)
    auction = mock.create_one_auction(db, [ticket])
    contractor = mock.create_one_contractor(db)
    nomination = mock.create_one_nomination(db, auction, contractor, approved=True)
    mgr_user = ticket.project.managers[0].user

    # now let's make the mgr a contractor and the contractor a mgr
    org_2 = mock.create_one_organization(db, user=contractor.user)
    project_2 = mock.create_one_github_project(db, organization=org_2)
    ticket_2 = mock.create_one_github_ticket(db, project=project_2)
    auction_2 = mock.create_one_auction(db, [ticket_2])
    contractor_2 = mock.create_one_contractor(db, user=mgr_user)
    nomination_2 = mock.create_one_nomination(db, auction, contractor_2, approved=True)

    db.session.commit()
    return mgr_user, contractor, auction, auction_2

def case_contractor(db):
    _, contractor, auction, _ = base_scenario(db)
    return contractor.user, auction

def case_mgr(db):
    mgr_user, _, auction, _ = base_scenario(db)
    return mgr_user, auction

def case_admin_base(db):
    _, _, auction, auction_2 = base_scenario(db)
    admin_user = mock.create_one_user(db)
    admin_user.admin = True
    db.session.commit()
    return admin_user, auction, auction_2

def case_admin(db):
    admin_user, auction, _ = case_admin_base(db)
    return admin_user, auction

def case_admin_collection(db):
    admin_user, auction, auction_2 = case_admin_base(db)
    return admin_user, [auction, auction_2]

def case_anonymous(db):
    _, _, _, _ = base_scenario(db)
    anonymous_user = mock.create_one_user(db)
    db.session.commit()
    return anonymous_user, None

