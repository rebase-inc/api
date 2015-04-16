from alveare import models
from alveare.common import mock

def case_manager_users(db):
    mgr_user = mock.create_one_user(db)
    org = mock.create_one_organization(db, 'Foo Inc.', mgr_user)
    mgr_1 = mock.create_one_manager(db, org=org)
    mgr_2 = mock.create_one_manager(db, org=org)
    db.session.commit()
    return (mgr_user, mgr_1, mgr_2)

def case_contractor_users(db):
    mgr_user = mock.create_one_user(db)
    org = mock.create_one_organization(db, 'Foo Inc.', mgr_user)
    project = mock.create_one_project(db, org, 'Bar Project')
    contractor_1 = mock.create_one_contractor(db)
    clearance_1 = mock.create_one_code_clearance(db, project, contractor_1)
    contractor_2 = mock.create_one_contractor(db)
    clearance_2 = mock.create_one_code_clearance(db, project, contractor_2)
    db.session.commit()
    return (mgr_user, contractor_1, contractor_2)
    
def case_nominated_users(db):
    mgr_user = mock.create_one_user(db)
    org = mock.create_one_organization(db, 'Foo Inc.', mgr_user)
    project = mock.create_one_project(db, org, 'Bar Project')
    project_tickets = [
        mock.create_one_internal_ticket(
            db,
            'Issue #{}'.format(i),
            project=project
        ) for i in range(10)
    ]
    auction = mock.create_one_auction(db, project_tickets)
    contractor_1 = mock.create_one_contractor(db)
    nomination_1 = mock.create_one_nomination(db, auction, contractor_1)
    contractor_2 = mock.create_one_contractor(db)
    nomination_2 = mock.create_one_nomination(db, auction, contractor_2)
    db.session.commit()
    return (mgr_user, contractor_1, contractor_2)
