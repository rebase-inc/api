from rebase import models
from rebase.common import mock
from rebase.common.utils import pick_an_organization_name

def case_mgr_with_repo(db):
    mgr_user = mock.create_one_user(db)
    org = mock.create_one_organization(db, pick_an_organization_name(), mgr_user)
    project = mock.create_one_project(db, org, 'Booze Project')
    db.session.commit()
    return mgr_user, project.work_repo

def case_cleared_contractor(db):
    mgr_user = mock.create_one_user(db)
    org = mock.create_one_organization(db, pick_an_organization_name(), mgr_user)
    project = mock.create_one_project(db, org, 'Booze Project')
    contractor = mock.create_one_contractor(db)
    clearance = mock.create_one_code_clearance(db, project, contractor)
    db.session.commit()
    return contractor.user, project.work_repo

