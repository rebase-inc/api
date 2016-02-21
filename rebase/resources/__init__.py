from collections import defaultdict
from functools import wraps, partial
from logging import warning
from sys import exc_info
from traceback import format_exc

from flask import current_app, jsonify, request
from flask.ext.restful import Resource
from flask.ext.login import login_required, current_user

from rebase.cache.rq_jobs import invalidate
from rebase.common.database import DB
from rebase.common.exceptions import ServerError, ClientError
from rebase.common.keys import get_model_primary_keys, make_collection_url, make_resource_url
from rebase.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource
from rebase.common.state import ManagedState


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
            warning(format_exc())
            raise ServerError(message='Server error')
    return _handle_other_exceptions


def default_to_None(handlers):
    _handlers = defaultdict(lambda : None)
    if handlers:
        _handlers.update(handlers)
    return _handlers


def _make_cache_key(old_make_cache_key, get_collection, model, serializer, role_id, handlers):
    prefix_hash = hash(str(model))
    return old_make_cache_key(get_collection, prefix_hash, role_id, handlers)


memoized_get_collection = current_app.redis.memoize(timeout=3600)(get_collection)
memoized_get_collection.make_cache_key = partial(_make_cache_key, memoized_get_collection.make_cache_key)


def RestfulCollection(model, serializer, deserializer, handlers=None, cache=False):
    '''
    Couldn't get metaclass to work for this, so we're cheating and using a func
    if 'cache' is True, GET will be cached into Redis
    '''
    _handlers = default_to_None(handlers)

    if cache:
        def get_all(role_id):
            return memoized_get_collection(model, serializer, role_id, handlers=_handlers['GET'])
        def clear_cache(role_id):
            current_app.redis.delete_memoized(memoized_get_collection, model, serializer, role_id, _handlers['GET'])
        setattr(get_all, 'clear_cache', clear_cache)
    else:
        def get_all(role_id):
            return get_collection(model, serializer, role_id, handlers=_handlers['GET'])

    class CustomRestfulCollection(Resource):

        @login_required
        @convert_exceptions
        def get(self):
            return get_all(current_user.current_role.id)

        @login_required
        @convert_exceptions
        def post(self):
            return add_to_collection(model, deserializer, serializer, handlers=_handlers['POST'])

    setattr(CustomRestfulCollection, 'get_all', get_all)
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


def add_restful_endpoint(api, model, serializer, deserializer, update_deserializer, cache=False):
    restful_collection = RestfulCollection(model, serializer, deserializer, cache=cache)
    restful_resource = RestfulResource(model, serializer, deserializer, update_deserializer)
    api.add_resource(restful_collection, make_collection_url(model), endpoint = model.__pluralname__)
    api.add_resource(restful_resource, make_resource_url(model), endpoint = model.__pluralname__ + '_resource')


class Event(Resource):
    model=None
    deserializer=None
    serializer=None

    @login_required
    def post(self, id):
        instance = self.model.query.get_or_404(id)
        event = self.deserializer.load(request.form or request.json).data

        with ManagedState():
            instance.machine.send(*event)

        DB.session.commit()

        # update the cache
        invalidate([(self.model, id)])

        response = jsonify({self.model.__tablename__: self.serializer.dump(instance).data})
        response.status_code = 201
        return response


