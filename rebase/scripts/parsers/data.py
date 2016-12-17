from subprocess import check_call

from flask_script import Manager, prompt_bool

from ...common.database import DB
from ...common import config


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
    from ...models import GithubOAuthApp
    github_app = GithubOAuthApp(config.GITHUB_APP_CLIENT_ID, 'skillviz',  config.PUBLIC_APP_URL)
    DB.session.add(github_app)
    DB.session.commit()


