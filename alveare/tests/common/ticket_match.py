from random import randrange
from rebase import models
from rebase.common import mock
from rebase.common.utils import pick_an_organization_name, pick_a_word

def base_scenario(db):
    mgr_user =      mock.create_one_user(db)
    org =           mock.create_one_organization(db, pick_an_organization_name(), mgr_user)
    project =       mock.create_one_github_project(db, org, pick_a_word().capitalize()+' Project')
    ticket =        mock.create_one_github_ticket(db, randrange(10*3, 10*4), project)
    contractor =    mock.create_one_contractor(db)
    clearance =     mock.create_one_code_clearance(db, project, contractor)
    ticket_matches = mock.create_ticket_matches(db, [ticket], contractor)

    db.session.commit()
    return mgr_user, contractor.user, ticket_matches[0]

def case_mgr(db):
    mgr_user, _, ticket_match = base_scenario(db)
    return mgr_user, ticket_match

def case_contractor(db):
    _, contractor_user, _ = base_scenario(db)
    return contractor_user, None

def case_admin(db):
    _, contractor_user, ticket_match = base_scenario(db)
    contractor_user.admin = True
    db.session.commit()
    return contractor_user, ticket_match
