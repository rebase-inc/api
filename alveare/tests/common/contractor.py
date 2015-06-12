from alveare import models
from alveare.common import mock

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

def case_cleared_contractors_as_contractor(db):
    mgr, all_contractors = case_cleared_contractors(db)

    contractor_0 = all_contractors[0]
    expected_contractors = [contractor_0, all_contractors[1], all_contractors[3]]
    return contractor_0.user, expected_contractors

def case_contractor_users(db):
    mgr_user = mock.create_one_user(db)
    org = mock.create_one_organization(db, 'Foo Inc.', mgr_user)
    project = mock.create_one_project(db, org, 'Bar Project')
    contractor_1 = mock.create_one_contractor(db)
    clearance_1 = mock.create_one_code_clearance(db, project, contractor_1)
    contractor_2 = mock.create_one_contractor(db)
    clearance_2 = mock.create_one_code_clearance(db, project, contractor_2)
    db.session.commit()
    return (mgr_user, [contractor_1.user, contractor_2.user])
    
def case_nominated_contractors(db):
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
    return (mgr_user, [contractor_1, contractor_2])

def case_managers_with_contractor(db):
    mgr_user = mock.create_one_user(db)
    org = mock.create_one_organization(db, 'Foo Inc.', mgr_user)
    mgr_1 = mock.create_one_manager(db, org=org)
    project = mock.create_one_project(db, org, 'Bar Project')
    contractor = mock.create_one_contractor(db)
    clearance = mock.create_one_code_clearance(db, project, contractor)
    db.session.commit()
    return (contractor.user, [mgr_user, mgr_1.user])

def case_contractors_with_contractor(db):
    mgr_user_1 = mock.create_one_user(db)
    mgr_user_2 = mock.create_one_user(db)
    org_1 = mock.create_one_organization(db, 'Foo Inc.', mgr_user_1)
    org_2 = mock.create_one_organization(db, 'Foo Inc.', mgr_user_2)
    project_1 = mock.create_one_project(db, org_1, 'Bar Project 1')
    project_2 = mock.create_one_project(db, org_2, 'Bar Project 2')
    contractor_1 = mock.create_one_contractor(db)
    contractor_2 = mock.create_one_contractor(db)
    contractor_3 = mock.create_one_contractor(db)
    mock.create_one_code_clearance(db, project_1, contractor_1)
    mock.create_one_code_clearance(db, project_1, contractor_2)
    mock.create_one_code_clearance(db, project_2, contractor_1)
    mock.create_one_code_clearance(db, project_2, contractor_3)
    db.session.commit()
    return (
        contractor_1.user,
        [
            mgr_user_1.roles.first().user,
            mgr_user_2.roles.first().user
        ],
        [
            contractor_1.user,
            contractor_2.user,
            contractor_3.user
        ]
    )
