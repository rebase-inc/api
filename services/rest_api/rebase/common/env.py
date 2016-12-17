from os import environ


class MissingEnvironmentVariables(Exception):
    error_message='Missing environment variables:\n{}'

    def __init__(self, missing):
        super().__init__(self.error_message.format(missing))


def check(variables):
    missing = tuple(filter(lambda var: var not in environ, variables))
    if missing:
        raise MissingEnvironmentVariables(missing)
