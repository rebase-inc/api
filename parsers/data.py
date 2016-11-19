from subprocess import check_call

from flask_script import Manager, prompt_bool

from rebase.common import mock
from rebase.common.database import DB
from rebase.common.settings import config


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
    from rebase.models import GithubOAuthApp
    alpha =         GithubOAuthApp(config['GITHUB_APP_ID'],         'alpha',        config['APP_URL'])
    code2resume =   GithubOAuthApp(config['GITHUB_CODE2RESUME_ID'], 'code2resume',  config['CODE2RESUME_URL'])
    DB.session.add(alpha)
    DB.session.add(code2resume)

    mock.DeveloperUserStory(DB, 'Phil Meyman', 'philmeyman@joinrebase.com', 'lem')
    mock.ManagerUserStory(DB, 'Ron Swanson', 'ron@joinrebase.com', 'ron')
    mock.create_one_user(DB, 'New User', 'new@joinrebase.com', 'new') 
    DB.session.commit()


