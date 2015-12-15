from os import environ

from rebase.common.exceptions import MissingEnvironmentVariables

def check(variables):
    missing = tuple(filter(lambda var: var not in environ, variables))
    if missing:
        raise MissingEnvironmentVariables(missing)
