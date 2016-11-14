from contextlib import contextmanager
from logging import getLogger
from os import chdir, getcwd


logger = getLogger(__name__)


@contextmanager
def cd(path):
    cwd = getcwd()
    chdir(path)
    logger.debug('changed to current working directory: '+getcwd())
    yield
    chdir(cwd)
    logger.debug('changed back to current working directory: '+getcwd())
