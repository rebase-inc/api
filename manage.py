#!/usr/bin/env python

from importlib import import_module
from pathlib import Path

from flask.ext.script import Manager, Command
from flask.ext.migrate import Migrate, MigrateCommand

from inflection import underscore

from alveare import create_app
import alveare.models

app, _, db = create_app()

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

for entry in Path('parsers').glob('*.py'):
    if entry.is_file() and not entry.name.startswith('__'):
        module = import_module('parsers.'+entry.stem)
        for attribute in dir(module):
            command = getattr(module, attribute)
            try:
                if not issubclass(command, Command) or command == Command:
                    continue
            except TypeError as e:
                if not isinstance(command, Manager):
                    continue
            manager.add_command(underscore(attribute), command)

@manager.shell
def make_shell_context():
        return dict(app=app, db=db, models=alveare.models)

if __name__ == '__main__':
    manager.run()
