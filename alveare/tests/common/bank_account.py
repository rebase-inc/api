from alveare import models
from alveare.common import mock
from alveare.common.utils import pick_an_organization_name

def case_contractors(db):
    contractor_0 = mock.create_one_contractor(db)
    mock.create_one_bank_account(db, contractor_0)
    contractor_1 = mock.create_one_contractor(db)
    mock.create_one_bank_account(db, contractor_1)
    db.session.commit()
    return [contractor_0, contractor_1]

def case_org(db):
    mgr_user = mock.create_one_user(db)
    org = mock.create_one_organization(db, pick_an_organization_name(), mgr_user)
    account = mock.create_one_bank_account(db, org)
    contractor = mock.create_one_contractor(db)
    project = mock.create_one_project(db, org, 'Bar Project')
    clearance = mock.create_one_code_clearance(db, project, contractor)
    db.session.commit()
    return mgr_user, org, account, contractor

