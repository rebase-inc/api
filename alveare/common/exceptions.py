from flask import jsonify
from contextlib import contextmanager
import marshmallow.exceptions
import alveare.common.exception_messages as messages

class AlveareError(Exception):
    code = 500

    def __init__(self, code, message=None, more_data=None):
        more_data = more_data or {}
        Exception.__init__(self)
        if code is not None:
            self.code = code
            self.data = {
                'status': code,
                'message': message or messages.HTTP_STATUS_CODES.get(code, '')
            }
        if isinstance(more_data, dict):
            self.data.update(more_data)
        else:
            raise Exception('Invalid data type: {}'.format(type(more_data)))

class ClientError(AlveareError):
    code = 400

    def __init__(self, code=None, message=None, more_data=None):
        super().__init__(code if code else self.code, message, more_data)

class InstanceNotFound(AlveareError):
    code = 404

    def __init__(self, code=None, __name=None, id=None, more_data=None):
        super().__init__(
            code if code else self.code,
            'No {__name} with id {id}'.format(__name, id),
            more_data
        )

class NoDataOrMissingIds(AlveareError):
    code = 400

    def __init__(self, code=None, model=None, more_data=None):
        super().__init__(
            code if code else self.code,
            'No data or valid ids provided to get/make {}!'.format(model),
            more_data
        )

class MarshmallowWrapperException(AlveareError):
    code = 500

    def __init__(self, exception_type, error_message, fields, error, data):
        if not isinstance(error, exception_type):
            raise ValueError(messages.expected_type.format(exception_type))
        msg_vars = [getattr(error, attribute) for attribute in fields] + [data]
        super().__init__(self.code, error_message.format(*msg_vars))

class MarshallingError(MarshmallowWrapperException):
    code = 400

    def __init__(self, error, data):
        super().__init__(
            marshmallow.exceptions.MarshallingError,
            messages.marshalling_error,
            ['field_name'],
            error,
            data
        )

class UnmarshallingError(MarshmallowWrapperException):
    code = 400

    def __init__(self, error, data):
        super().__init__(
            marshmallow.exceptions.UnmarshallingError,
            messages.unmarshalling_error,
            ['field_name'],
            error,
            data
        )

class ValidationError(MarshmallowWrapperException):
    code = 400

    def __init__(self, error, data):
        super().__init__(
            marshmallow.exceptions.ValidationError,
            messages.validation_error,
            ['field'],
            error,
            data
        )

class ForcedError(MarshmallowWrapperException):
    code = 400

    def __init__(self, error, data):
        super().__init__(
            marshmallow.exceptions.ForcedError,
            messages.forced_error,
            ['field'],
            error,
            data
        )

@contextmanager
def marshmallow_exceptions(data=None):
    try:
        yield

    except marshmallow.exceptions.MarshallingError as error:
        raise MarshallingError(error, data)

    except marshmallow.exceptions.UnmarshallingError as error:
        raise UnmarshallingError(error, data)

    except marshmallow.exceptions.ValidationError as error:
        raise ValidationError(error, data)

    except marshmallow.exceptions.ForcedError as error:
        raise ForcedError(error, data)
