
from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare.models import BankAccount
from alveare.views import bank_account
from alveare.common.database import DB
from alveare.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource


class BankAccountCollection(Resource):
    model = BankAccount
    serializer = bank_account.serializer
    deserializer = bank_account.deserializer
    url = '/{}'.format(model.__pluralname__)
    
    def get(self): 
        return get_collection(self.model, self.serializer)
    def post(self): 
        return add_to_collection(self.model, self.deserializer, self.serializer)

class BankAccountResource(Resource):
    model = BankAccount
    serializer = bank_account.serializer
    deserializer = bank_account.deserializer
    update_deserializer = bank_account.update_deserializer
    url = '/{}/<int:id>'.format(model.__pluralname__)
    
    def get(self, id): 
        return get_resource(self.model, id, self.serializer)
    def put(self, id): 
        return update_resource(self.model, id, self.update_deserializer, self.serializer) 
    def delete(self, id): 
        return delete_resource(self.model, id)
