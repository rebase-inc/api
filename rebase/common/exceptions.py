from contextlib import contextmanager
from sys import exc_info

from flask import jsonify
import marshmallow.exceptions as marsh_exc
from werkzeug.http import HTTP_STATUS_CODES

LAUNCH_DEBUGGER=False

class RebaseError(Exception):
    def __init__(self, code, default_message, message=None, more_data=None):
        if LAUNCH_DEBUGGER:
            import pdb; pdb.set_trace()
        more_data = more_data or {}
        self.code = code
        self.data = {
            'status': code,
            'message': message or HTTP_STATUS_CODES.get(code, default_message)
        }
        if isinstance(more_data, dict):
            self.data.update(more_data)
        super().__init__(self)

    def __str__(self):
        return str({'code': self.code, 'data': self.data})

class ClientError(RebaseError):
    def __init__(self, code=400, message=None, more_data=None):
        super().__init__(code, 'Client Error', message=message, more_data=more_data)


class ServerError(RebaseError):
    def __init__(self, code=500, message=None, more_data=None):
        super().__init__(code, 'Server Error', message=message, more_data=more_data)


class NotFoundError(ClientError):
    def __init__(self, name, id, more_data=None):
        message = "No {} with id {}".format(name, id)
        super().__init__(code=404, message=message, more_data=more_data)


class BadDataError(ClientError):
    def __init__(self, code=400, model_name=None, more_data=None):
        message = "No data or valid ids provided to get/make {}!".format(model_name),
        super().__init__(code=code, message=message, more_data=more_data)


class MarshallingError(ServerError):
    def __init__(self, error, data):
        if not isinstance(error, marsh_exc.MarshallingError):
            raise ValueError('error parameter must be of type {}'.format(marsh_exc.MarshallingError))
        error_message = '{}\nin data:\n{}'.format(str(error), data)
        super().__init__(message=error_message, more_data=data)


class UnmarshallingError(ClientError):
    def __init__(self, error, data):
        if not isinstance(error, marsh_exc.UnmarshallingError):
            raise ValueError('error parameter must be of type {}'.format(marsh_exc.UnmarshallingError))
        error_message = '{}\nin data:\n{}'.format(str(error), data)
        super().__init__(message=error_message, more_data=data)


class ValidationError(ClientError):
    def __init__(self, error, data):
        if not isinstance(error, marsh_exc.ValidationError):
            raise ValueError('error parameter must be of type {}'.format(marsh_exc.ValidationError))
        error_message = "Validation error: '{}' while validating: {}"
        error_message = error_message.format(error.field, data)
        super().__init__(message=error_message, more_data=data)


class ForcedError(ServerError):
    def __init__(self, error, data):
        if not isinstance(error, marsh_exc.ForcedError):
            raise ValueError('error parameter must be of type {}'.format(marsh_exc.ForcedError))
        error_message = str(error)
        super().__init__(message=error_message, more_data=data)


class InternalTypeError(ServerError):
    def __init__(self, error, data):
        if not isinstance(error, TypeError):
            raise ValueError('error parameter must be of type {}'.format(TypeError))
        error_message = str(error)
        super().__init__(message=error_message, more_data=data)


class NoRole(ServerError):
    error_message = 'User[{}] should have an associated role'

    def __init__(self, user):
        super().__init__(message=NoRole.error_message.format(user.id))


class UnknownRole(ServerError):
    error_message = 'Unknown role: {}'

    def __init__(self, role):
        super().__init__(message=UnknownRole.error_message.format(role))


class QueryPathUndefined(TypeError):
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
    error_message = 'bid didnt match expected tickets! we needed {} but got {}'
    def __init__(self, required_tickets, bid_tickets):
        super().__init__(message=self.error_message.format(required_tickets, bid_tickets))

class AlreadyBid(ClientError):
    error_message = '{} already bid for {}'
    
    def __init__(self, contractor, ticket_snapshot):
        super().__init__(code=409, message=self.error_message.format(contractor, ticket_snapshot))

@contextmanager
def marshmallow_exceptions(data=None):
    try:
        yield
    except marsh_exc.MarshallingError as error:
        raise MarshallingError(error, data)
    except marsh_exc.UnmarshallingError as error:
        raise UnmarshallingError(error, data)
    except marsh_exc.ValidationError as error:
        raise ValidationError(error, data)
    except marsh_exc.ForcedError as error:
        raise ForcedError(error, data)
    except TypeError as error:
        raise InternalTypeError(error, data)

