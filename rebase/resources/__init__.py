from collections import defaultdict
from functools import wraps
from sys import exc_info

from flask.ext.restful import Resource
from flask.ext.login import login_required

from rebase.common.database import get_model_primary_keys, make_collection_url, make_resource_url
from rebase.common.exceptions import ServerError, ClientError
from rebase.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource

def convert_exceptions(verb):
    @wraps(verb)
    def _handle_other_exceptions(*args, **kwargs):
        try:
            return verb(*args, **kwargs)
        except ServerError as server_error:
            raise server_error
        except ClientError as client_error:
            raise client_error
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise ServerError(message='Server error')
    return _handle_other_exceptions

def default_to_None(handlers):
    _handlers = defaultdict(lambda : None)
    if handlers:
        _handlers.update(handlers)
    return _handlers

def RestfulCollection(model, serializer, deserializer, handlers=None):
    ''' Couldn't get metaclass to work for this, so we're cheating and using a func '''
    _handlers = default_to_None(handlers)
    class CustomRestfulCollection(Resource):
        @login_required
        @convert_exceptions
        def get(self):
            return get_collection(model, serializer, handlers=_handlers['GET'])
        @login_required
        @convert_exceptions
        def post(self):
            return add_to_collection(model, deserializer, serializer, handlers=_handlers['POST'])

    return CustomRestfulCollection

def RestfulResource(model, serializer, deserializer, update_deserializer, handlers=None):
    _handlers = default_to_None(handlers)
    class CustomRestfulResource(Resource):
        @login_required
        @convert_exceptions
        def get(self, **id_args):
            id_values = tuple(id_args[pk] for pk in get_model_primary_keys(model))
            return get_resource(model, id_values, serializer, handlers=_handlers['GET'])
        @login_required
        @convert_exceptions
        def put(self, **id_args):
            id_values = tuple(id_args[pk] for pk in get_model_primary_keys(model))
            return update_resource(model, id_values, update_deserializer, serializer, handlers=_handlers['PUT'])
        @login_required
        @convert_exceptions
        def delete(self, **id_args):
            id_values = tuple(id_args[pk] for pk in get_model_primary_keys(model))
            return delete_resource(model, id_values, handlers=_handlers['DELETE'])

    return CustomRestfulResource

def add_restful_endpoint(api, model, serializer, deserializer, update_deserializer):
    restful_collection = RestfulCollection(model, serializer, deserializer)
    restful_resource = RestfulResource(model, serializer, deserializer, update_deserializer)
    api.add_resource(restful_collection, make_collection_url(model), endpoint = model.__pluralname__)
    api.add_resource(restful_resource, make_resource_url(model), endpoint = model.__pluralname__ + '_resource')
