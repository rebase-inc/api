
from flask.ext.restful import Resource
from flask import jsonify, make_response, request
from alveare.common.database import DB
from alveare.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource
from alveare.common.utils import collection_url, resource_url

def make_collection_and_resource_classes(
    Model,
    serializer,
    deserializer,
    update_deserializer
):
    class AlveareCollection(Resource):
        def get(self):
            return get_collection(Model, serializer)
        def post(self):
            return add_to_collection(Model, deserializer, serializer)

    class AlveareResource(Resource):
        def get(self, id):
            return get_resource(Model, id, serializer)
        def put(self, id):
            return update_resource(Model, id, update_deserializer, serializer)
        def delete(self, id):
            return delete_resource(Model, id)
    
    return AlveareCollection, AlveareResource

def add_alveare_resource(
    api,
    Model,
    serializer,
    deserializer,
    update_deserializer
):
    '''
    Declares a new resource for the Model, and adds 2 paths: one for a collection,
    the other for a single resource.

    api is a Flask api object.
    Model is a SqlAlchemy Model class.
    serializer, deserializer, update_serializer map to GET, POST, PUT respectively.

    TODO: this could be abstracted more using 2 maps of HTTP verbs (one for the collection, one for a single resource)
    '''

    ModelCollection, ModelResource = make_collection_and_resource_classes(
        Model,
        serializer,
        deserializer,
        update_deserializer
    )
    api.add_resource(ModelCollection, collection_url(Model), endpoint=Model.__pluralname__)
    api.add_resource(ModelResource, resource_url(Model, use_flask_format=True), endpoint=Model.__tablename__)
