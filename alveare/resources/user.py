
from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare.models import User
from alveare.views import user
from alveare.common.database import DB
from alveare.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource

class UserCollection(Resource):
    model = User
    serializer = user.serializer
    deserializer = user.deserializer
    url = '/{}'.format(model.__pluralname__)
    
    def get(self): 
        return get_collection(self.model, self.serializer)
    def post(self): 
        return add_to_collection(self.model, self.deserializer, self.serializer)

class UserResource(Resource):
    model = User
    serializer = user.serializer
    deserializer = user.deserializer
    update_deserializer = user.update_deserializer
    url = '/{}/<int:id>'.format(model.__pluralname__)
    
    def get(self, id): 
        return get_resource(self.model, id, self.serializer)
    def put(self, id): 
        return update_resource(self.model, id, self.update_deserializer, self.serializer) 
    def delete(self, id): 
        return delete_resource(self.model, id)
