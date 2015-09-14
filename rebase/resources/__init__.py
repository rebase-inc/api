
from flask.ext.restful import Resource
from flask.ext.login import login_required
from rebase.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource
from rebase.common.utils import make_collection_url, make_resource_url, get_model_primary_keys

def RestfulCollection(model, serializer, deserializer):
    ''' Couldn't get metaclass to work for this, so we're cheating and using a func '''
    class CustomRestfulCollection(Resource):
        @login_required
        def get(self):
            return get_collection(model, serializer)
        @login_required
        def post(self):
            return add_to_collection(model, deserializer, serializer)

    return CustomRestfulCollection

def RestfulResource(model, serializer, deserializer, update_deserializer):
    class CustomRestfulResource(Resource):
        @login_required
        def get(self, **id_args):
            id_values = tuple(id_args[pk] for pk in get_model_primary_keys(model))
            return get_resource(model, id_values, serializer)
        @login_required
        def put(self, **id_args):
            id_values = tuple(id_args[pk] for pk in get_model_primary_keys(model))
            return update_resource(model, id_values, update_deserializer, serializer)
        @login_required
        def delete(self, **id_args):
            id_values = tuple(id_args[pk] for pk in get_model_primary_keys(model))
            return delete_resource(model, id_values)

    return CustomRestfulResource

def add_restful_endpoint(api, model, serializer, deserializer, update_deserializer, foo=None):
    restful_collection = RestfulCollection(model, serializer, deserializer)
    restful_resource = RestfulResource(model, serializer, deserializer, update_deserializer)
    api.add_resource(restful_collection, make_collection_url(model), endpoint = model.__pluralname__)
    api.add_resource(restful_resource, make_resource_url(model), endpoint = model.__pluralname__ + '_resource')
