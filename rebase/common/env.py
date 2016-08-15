from os import environ


class MissingEnvironmentVariables(Exception):
    error_message='Missing environment variables:\n{}\nDid you forget to run "source setup.sh" or "source test_setup.sh"?'

    def __init__(self, missing):
        super().__init__(message=self.error_message.format(missing))


def check(variables):
    missing = tuple(filter(lambda var: var not in environ, variables))
    if missing:
        raise MissingEnvironmentVariables(missing)
