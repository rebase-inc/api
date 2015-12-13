from contextlib import contextmanager
from inspect import isclass
from pprint import pformat
from sys import modules

import marshmallow.exceptions as marsh_exc
from werkzeug.http import HTTP_STATUS_CODES


class RebaseError(Exception):
    '''
    For all RebaseError exceptions:
    status is the HTTP status code return in the Flask response when this exception is raised.
    message is the string sent to the HTTP client.
    '''
    status=500
    message=HTTP_STATUS_CODES[500]

    def __init__(self, message=None):
        self.data = {
            'status': self.status,
            'message': message or self.message 
        }
        super().__init__()

    def __str__(self):
        return str({'status': self.status, 'data': self.data})

ServerError=RebaseError

class ClientError(RebaseError):
    status=400
    message=HTTP_STATUS_CODES[400]


class NotFoundError(ClientError):
    status=404
    message=HTTP_STATUS_CODES[404]

    def __init__(self, name, id):
        message = "No {} with id {}".format(name, id)
        super().__init__(message=message)


class BadDataError(ClientError):
    message = "Serialization/deserialization error: no data or valid ids provided to get/make"

    def __init__(self, model_name=None):
        message = self.message+' for model: {}'.format(model_name)
        super().__init__(message=message)


class ValidationError(ClientError):
    message='Validation error in deserialization'

    def __init__(self, error, data):
        if not isinstance(error, marsh_exc.ValidationError):
            raise ValueError('error parameter must be of type {}'.format(marsh_exc.ValidationError))
        super().__init__(message=self.message+': '+pformat(error.messages))


@contextmanager
def marshmallow_exceptions(data=None):
    try:
        yield
    except marsh_exc.ValidationError as error:
        raise ValidationError(error, data)
    except Exception as error:
        import traceback
        traceback.print_exc()
        raise ServerError(message=str(error))

class NoRole(ServerError):
    error_message = 'User[{}] should have an associated role'

    def __init__(self, user):
        super().__init__(message=NoRole.error_message.format(user.id))


class UnknownRole(ServerError):
    message='Unknown role'
    error_message = message+': {}'

    def __init__(self, role):
        super().__init__(message=UnknownRole.error_message.format(role))


class InvalidGithubAccessToken(ServerError):
    message='Invalid Github Access Token'
    error_message = 'Invalid Github Access Token for {} for Github login: {}'

    def __init__(self, user, login):
        super().__init__(message=self.error_message.format(user, login))


class QueryPathUndefined(ServerError):
    path_field_name = None
    error_message = 'You need to provide a valid list for {}.{}'

    def __init__(self, klass):
        if not self.path_field_name:
            raise NotImplementedError('Invalid exception {}, missing value for class field path_field_name'.format(self.__class__.__name__))
        super().__init__(self.error_message.format(klass.__name__, self.path_field_name))


class AsManagerPathUndefined(QueryPathUndefined):
    path_field_name = 'as_manager_path'


class AsContractorPathUndefined(QueryPathUndefined):
    path_field_name = 'as_contractor_path'


class AsOwnerPathUndefined(QueryPathUndefined):
    path_field_name = 'as_owner_path'


class BadBid(ClientError):
    message='Bid did not match expected set of tickets'
    error_message = 'bid didnt match expected tickets! we needed {} but got {}'

    def __init__(self, required_tickets, bid_tickets):
        super().__init__(message=self.error_message.format(required_tickets, bid_tickets))


class AlreadyBid(ClientError):
    status=409
    message='Contractor already bid for this ticket'
    error_message = 'Contractor "{}" already bid for Ticket "{}"'

    def __init__(self, contractor, ticket_snapshot):
        super().__init__(message=self.error_message.format(contractor.user.name, ticket_snapshot.title))


class Forbidden(ClientError):
    status=403
    message=HTTP_STATUS_CODES[403]


class MissingEnvironmentVariables(ServerError):
    status=500
    message='Missing Environment Variables'
    error_message='Missing environment variables:\n{}\nDid you forget to run "source setup.sh" or "source test_setup.sh"?'

    def __init__(self, missing):
        super().__init__(message=self.error_message.format(missing))


loaded_references = modules[__name__].__dict__.copy()
exceptions = filter(lambda thing: isclass(thing) and issubclass(thing, RebaseError), loaded_references.values())

errors = {
    exception.__name__: {
        'message': exception.message,
        'status': exception.status
    }
    for exception in exceptions
}
