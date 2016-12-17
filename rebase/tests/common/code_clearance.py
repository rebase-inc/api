from rebase import models
from rebase.common import mock

def case_cleared_contractors(db):
    mgr_user = mock.create_one_user(db)
    org = mock.create_one_organization(db, 'Foo Inc.', mgr_user)
    project_1 = mock.create_one_project(db, org, 'Bar Project')
    project_2 = mock.create_one_project(db, org, 'Bozo Project')
    project_3 = mock.create_one_project(db, org, 'Mayhem Project')
    contractor_1 = mock.create_one_contractor(db)
    clearance_1 = mock.create_one_code_clearance(db, project_1, contractor_1)
    contractor_2 = mock.create_one_contractor(db)
    clearance_2 = mock.create_one_code_clearance(db, project_1, contractor_2)
    contractor_3 = mock.create_one_contractor(db)
    clearance_3 = mock.create_one_code_clearance(db, project_2, contractor_3)
    contractor_4 = mock.create_one_contractor(db)
    clearance_4 = mock.create_one_code_clearance(db, project_3, contractor_4)
    clearance_5 = mock.create_one_code_clearance(db, project_3, contractor_1)
    db.session.commit()
    return (mgr_user, [contractor_1, contractor_2, contractor_3, contractor_4])
