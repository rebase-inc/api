from importlib import import_module
from pathlib import Path

from flask_script import Manager, Command
from flask_migrate import Migrate, MigrateCommand

from inflection import underscore

from ..app import create
from ..common.database import DB
import rebase.models

from .parsers.data import data

app = create()


migrate = Migrate(app, DB)


manager = Manager(app)


manager.add_command('db', MigrateCommand)


manager.add_command('data', data)


@manager.shell
def make_shell_context():
    return dict(app=app, db=DB, models=rebase.models)


if __name__ == '__main__':
    manager.run()


