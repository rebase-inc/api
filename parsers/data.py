from subprocess import check_call

from flask.ext.script import Manager, prompt_bool

from rebase.app import create as create_app
from rebase.common import mock
from rebase.common.database import DB


app = create_app()

data = Manager(usage="Manage the data inside the database.")

@data.option('-y', '--yes', action='store_true')
def drop(yes):
    "Drops database tables"
    if yes or prompt_bool("Are you sure you want to lose all your data?"):
        DB.drop_all()


@data.command
def create():
    "Creates database tables from sqlalchemy models"
    DB.create_all()


@data.option('-y', '--yes', action='store_true')
def recreate(yes):
    "Recreates database tables (same as issuing 'drop' and then 'create')"
    drop(yes)
    create()


@data.command
def populate():
    "Populate database with default data"
    mock.DeveloperUserStory(DB, 'Phil Meyman', 'philmeyman@joinrebase.com', 'lem')
    mock.ManagerUserStory(DB, 'Ron Swanson', 'ron@joinrebase.com', 'ron')
    mock.create_one_user(DB, 'New User', 'new@joinrebase.com', 'new') 
    DB.session.commit()


