from __future__ import with_statement
from logging import warning
from logging.config import fileConfig
from multiprocessing import current_process
from os import getcwd
from os.path import abspath, join
import sys
from threading import current_thread

from alembic import context
from sqlalchemy import engine_from_config, pool

# clarifies log entries by setting actual names instead of anonymous processes and threads
current_process().name='Alembic'
current_thread().name='env.py'

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

parent_dir = abspath(getcwd())
sys.path.append(parent_dir)
import rebase.models
# we could not use create and import DB directly
# but with create, any log entry will be sent to rsyslog container
from rebase.app import create
_, _, DB = create()
target_metadata = DB.Model.metadata
if(len(target_metadata.tables) == 0):
    warning('''
    No table detected.
    You can ignore this warning if your code does not have any model created yet.
    If it does, you must import these models before you attempt to set the target_metadata.
    Otherwise, the autogeneration of revision will not work as you would expect!
    ''')

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
