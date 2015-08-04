from random import randrange
from rebase import models
from rebase.common import mock
from rebase.common.utils import pick_an_organization_name, pick_a_word

def base_scenario(db):
    mgr_user =      mock.create_one_user(db)
    org =           mock.create_one_organization(db, pick_an_organization_name(), mgr_user)
    project =       mock.create_one_github_project(db, org, pick_a_word().capitalize()+' Project')
    contractor =    mock.create_one_contractor(db)
    clearance =     mock.create_one_code_clearance(db, project, contractor)

    db.session.commit()
    return mgr_user, contractor.user, contractor.skill_set

def case_mgr(db):
    mgr_user, _, skill_set = base_scenario(db)
    return mgr_user, skill_set

def case_contractor(db):
    _, contractor_user, skill_set = base_scenario(db)
    return contractor_user, skill_set

def case_admin(db):
    _, contractor_user, skill_set = base_scenario(db)
    contractor_user.admin = True
    db.session.commit()
    return contractor_user, skill_set
