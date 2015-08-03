from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from alveare import create_app

app, _, db = create_app()

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
