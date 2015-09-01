
from rebase.common.mock import create_one_user

from .ticket import base_scenario

def case_contractor(db):
    _, contractor, ticket = base_scenario(db, 'github')
    return contractor.user, ticket

def case_mgr(db):
    mgr_user, _, ticket = base_scenario(db, 'github')
    return mgr_user, ticket

def case_admin(db):
    _, _, ticket = base_scenario(db, 'github')
    admin_user = create_one_user(db)
    admin_user.admin = True
    db.session.commit()
    return admin_user, ticket

def case_anonymous(db):
    _, _, ticket = base_scenario(db, 'github')
    anonymous_user = create_one_user(db)
    db.session.commit()
    return anonymous_user, ticket
