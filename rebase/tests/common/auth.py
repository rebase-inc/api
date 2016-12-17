from math import floor

from rebase import models
from rebase.common import mock
from rebase.common.utils import pick_an_organization_name

def create_user(db):
    ''' creates a user that is both a manager and a contractor '''
    user = mock.create_one_user(db)
    org = mock.create_one_organization(db, pick_an_organization_name(), user)
    contractor = mock.create_one_contractor(db, user=user)
    db.session.commit()
    return user
