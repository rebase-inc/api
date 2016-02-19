from subprocess import check_call

from flask.ext.script import Manager, prompt_bool

from rebase.app import create
from rebase.common import mock
_, _, db = create()

data = Manager(usage="Manage the data inside the database.")

@data.option('-y', '--yes', action='store_true')
def drop(yes):
    "Drops database tables"
    if yes or prompt_bool("Are you sure you want to lose all your data?"):
        db.drop_all()


@data.command
def create():
    "Creates database tables from sqlalchemy models"
    db.create_all()


@data.option('-y', '--yes', action='store_true')
def recreate(yes):
    "Recreates database tables (same as issuing 'drop' and then 'create')"
    drop(yes)
    create()


@data.command
def populate():
    "Populate database with default data"
    mock.DeveloperUserStory(db, 'Phil Meyman', 'philmeyman@joinrebase.com', 'lem')
    mock.ManagerUserStory(db, 'Ron Swanson', 'ron@joinrebase.com', 'ron')
    mock.create_one_user(db, 'New User', 'new@joinrebase.com', 'new') 

    db.session.commit()
