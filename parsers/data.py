from subprocess import check_call

from flask.ext.script import Manager, prompt_bool

from rebase import create_app
from rebase.common import mock
_, _, db = create_app()

data = Manager(usage="Manage the data inside the database.")

@data.command
def wipe_out(yes=False):
    '''
    Deletes and recreates the entire database using psql directly.
    Use it if 'data recreate' fails because the database needs to be migrated.
    The command will prompt for confirmation unless the '--yes' option is provided
    to override the prompt.

    Example usage: 
    ./manage data wipe_out --yes
    ./manage data create
    ./manage data populate
    '''
    if not yes:
        if not prompt_bool("Are you sure you want to lose all your data?"):
            return
    database_name = 'rebase_web'
    check_call(['dropdb', database_name])
    check_call(['createdb', database_name])


@data.command
def drop():
    "Drops database tables"
    if prompt_bool("Are you sure you want to lose all your data?"):
        db.drop_all()


@data.command
def create(default_data=True, sample_data=False):
    "Creates database tables from sqlalchemy models"
    db.create_all()


@data.command
def recreate(default_data=True, sample_data=False):
    "Recreates database tables (same as issuing 'drop' and then 'create')"
    drop()
    create(default_data, sample_data)


@data.command
def populate(default_data=False, sample_data=False):
    "Populate database with default data"
    dev_user_story = mock.DeveloperUserStory(db, 'Phil', 'Meyman', 'philmeyman@joinrebase.com', 'lem')
    dev_user_story = mock.ManagerUserStory(db, 'Ron', 'Swanson', 'ron@joinrebase.com', 'ron')

    db.session.commit()
