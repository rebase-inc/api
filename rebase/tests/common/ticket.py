from functools import partial
from random import randrange

from rebase import models
from rebase.common import mock
from rebase.common.utils import pick_an_organization_name, pick_a_word

proj = {
    'github': {
        'project': mock.create_one_github_project,
        'ticket': mock.create_one_github_ticket,
    },
    'internal': {
        'project': mock.create_one_project,
        'ticket': mock.create_one_internal_ticket,
    },
}

def base_scenario(db, project_type):
    fns = proj[project_type]
    ticket = fns['ticket'](db)
    contractor = mock.create_one_contractor(db)
    clearance = mock.create_one_code_clearance(db, ticket.project, contractor)
    mgr_user = ticket.project.organization.managers[0].user

    #let's make this contractor the manager for another org for which mgr_user is a contractor
    # This is to make sure the queries are properly discrimitating based on the current role
    org_2 = mock.create_one_organization(db, user=contractor.user)
    project_2 = fns['project'](db, organization=org_2)
    ticket_2 = fns['ticket'](db, project=project_2)
    contractor_2 = mock.create_one_contractor(db, mgr_user)
    clearance_2 = mock.create_one_code_clearance(db, project_2, contractor_2)

    db.session.commit()
    return mgr_user, contractor, ticket, ticket_2

def case_contractor(db, project_type):
    _, contractor, ticket, _ = base_scenario(db, project_type)
    return contractor.user, ticket

def case_mgr(db, project_type):
    mgr_user, _, ticket, _ = base_scenario(db, project_type)
    return mgr_user, ticket

def case_admin_base(db, project_type):
    _, _, ticket, ticket_2 = base_scenario(db, project_type)
    admin_user = mock.create_one_user(db)
    admin_user.admin = True
    db.session.commit()
    return admin_user, ticket, ticket_2

def case_admin(db, project_type):
    admin_user, ticket, _ = case_admin_base(db, project_type)
    return admin_user, ticket

def case_admin_collection(db, project_type):
    admin_user, ticket, ticket_2 = case_admin_base(db, project_type)
    return admin_user, [ticket, ticket_2]

def case_anonymous_base(db, project_type):
    _, _, ticket, _ = base_scenario(db, project_type)
    anonymous_user = mock.create_one_user(db)
    db.session.commit()
    return anonymous_user, ticket

def case_anonymous(db, project_type):
    return case_anonymous_base(db, project_type)

def case_anonymous_collection(db, project_type):
    anonymous_user, _ = case_anonymous_base(db, project_type)
    return anonymous_user, []

case_internal_contractor =          partial(case_contractor,        project_type='internal')
case_internal_mgr =                 partial(case_mgr,               project_type='internal')
case_internal_admin_base =          partial(case_admin_base,        project_type='internal')
case_internal_admin =               partial(case_admin,             project_type='internal')
case_internal_admin_collection =    partial(case_admin_collection,  project_type='internal')
case_internal_anonymous =           partial(case_anonymous,         project_type='internal')
case_internal_anonymous_collection =partial(case_anonymous_collection, project_type='internal')

case_github_contractor =            partial(case_contractor,        project_type='github')
case_github_mgr =                   partial(case_mgr,               project_type='github')
case_github_admin_base =            partial(case_admin_base,        project_type='github')
case_github_admin =                 partial(case_admin,             project_type='github')
case_github_admin_collection =      partial(case_admin_collection,  project_type='github')
case_github_anonymous =             partial(case_anonymous,         project_type='github')
case_github_anonymous_collection =  partial(case_anonymous_collection,         project_type='github')
