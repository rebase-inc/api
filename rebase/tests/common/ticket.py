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
    'remote': {
        'project': mock.create_one_remote_project,
        'ticket': mock.create_one_remote_ticket,
    },
}

def base_scenario(db, project_type):
    mgr_user = mock.create_one_user(db)
    org = mock.create_one_organization(db, user=mgr_user)
    fns = proj[project_type]
    project = fns['project'](db, organization=org)
    ticket = fns['ticket'](db, project=project)
    contractor = mock.create_one_contractor(db)
    clearance = mock.create_one_code_clearance(db, project, contractor)
    db.session.commit()
    return mgr_user, contractor, ticket

def case_contractor(db):
    _, contractor, ticket = base_scenario(db, 'internal')
    return contractor.user, ticket

def case_mgr(db):
    mgr_user, _, ticket = base_scenario(db, 'internal')
    return mgr_user, ticket

def case_admin(db):
    _, _, ticket = base_scenario(db, 'internal')
    admin_user = mock.create_one_user(db)
    admin_user.admin = True
    db.session.commit()
    return admin_user, ticket

def case_anonymous(db):
    _, _, ticket = base_scenario(db, 'internal')
    anonymous_user = mock.create_one_user(db)
    db.session.commit()
    return anonymous_user, ticket
