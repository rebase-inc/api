from flask import jsonify
from contextlib import contextmanager
import marshmallow.exceptions as marsh_exc
from werkzeug.http import HTTP_STATUS_CODES

LAUNCH_DEBUGGER=False

class ClientError(Exception):
    def __init__(self, code=400, message=None, more_data=None):
        if LAUNCH_DEBUGGER:
            import pdb; pdb.set_trace()
        more_data = more_data or {}
        self.code = code
        self.data = {
            'status': code,
            'message': message or HTTP_STATUS_CODES.get(code, 'Client Error')
        }
        if isinstance(more_data, dict):
            self.data.update(more_data)
        super().__init__(self)

class NotFoundError(ClientError):
    def __init__(self, name, id, more_data=None):
        message = "No {} with id {}".format(name, id)
        super().__init__(code=404, message=message, more_data=more_data)

class BadDataError(ClientError):
    def __init__(self, code=400, model_name=None, more_data=None):
        message = "No data or valid ids provided to get/make {}!".format(model_name),
        super().__init__(code, message, more_data)

class MarshallingError(ClientError):
    def __init__(self, error, data):
        if not isinstance(error, marsh_exc.MarshallingError):
            raise ValueError('error parameter must be of type {}'.format(marsh_exc.MarshallingError))
        error_message = "Missing field '{}' while serializing: {}"
        error_message = error_message.format(error.field_name, data)
        super().__init__(400, error_message)

class UnmarshallingError(ClientError):
    def __init__(self, error, data):
        if not isinstance(error, marsh_exc.UnmarshallingError):
            raise ValueError('error parameter must be of type {}'.format(marsh_exc.UnmarshallingError))
        error_message = "Missing field: '{}' while deserializing: {}"
        error_message = error_message.format(error.field_name, data)
        super().__init__(400, error_message)

class ValidationError(ClientError):
    def __init__(self, error, data):
        if not isinstance(error, marsh_exc.ValidationError):
            raise ValueError('error parameter must be of type {}'.format(marsh_exc.ValidationError))
        error_message = "Validation error: '{}' while validating: {}"
        error_message = error_message.format(error.field, data)
        super().__init__(400, error_message)

class ForcedError(ClientError):
    def __init__(self, error, data):
        if not isinstance(error, marsh_exc.ForcedError):
            raise ValueError('error parameter must be of type {}'.format(marsh_exc.ForcedError))
        error_message = "Forced error: '{}' while validating: {}"
        error_message = error_message.format(error.field_name, data)
        super().__init__(400, error_message)


class ServerError(Exception):
    def __init__(self, code=500, message=None, more_data=None):
        if LAUNCH_DEBUGGER:
            import pdb; pdb.set_trace()
        more_data = more_data or {}
        self.code = code
        self.data = {
            'status': code,
            'message': message or HTTP_STATUS_CODES.get(code, 'Server Error')
        }
        if isinstance(more_data, dict):
            self.data.update(more_data)
        super().__init__(self)

class NoRole(ServerError):
    error_message = 'User[{}] should have an associated role'

    def __init__(self, user):
        super().__init__(message=NoRole.error_message.format(user.id))

class UnknownRole(ServerError):
    error_message = 'Unknown role: {}'

    def __init__(self, role):
        super().__init__(message=UnknownRole.error_message.format(role))


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
