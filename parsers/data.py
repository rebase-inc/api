from flask.ext.script import Manager, prompt_bool


from rebase import create_app
from rebase.common import mock
_, _, db = create_app()

data = Manager(usage="Manage the data inside the database.")

@data.command
def drop():
    "Drops database tables"
    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()


@data.command
def create(default_data=True, sample_data=False):
    "Creates database tables from sqlalchemy models"
    db.create_all()
    populate(default_data, sample_data)


@data.command
def recreate(default_data=True, sample_data=False):
    "Recreates database tables (same as issuing 'drop' and then 'create')"
    drop()
    create(default_data, sample_data)


@data.command
def populate(default_data=False, sample_data=False):
    "Populate database with default data"
    mock.create_the_world(db)
    db.session.commit()
    #from fixtures import dbfixture

    #if default_data:
        #from fixtures.default_data import all
        #default_data = dbfixture.data(*all)
        #default_data.setup()

    #if sample_data:
        #from fixtures.sample_data import all
        #sample_data = dbfixture.data(*all)
        #sample_data.setup()
