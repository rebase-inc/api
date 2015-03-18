
from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare.models import BidLimit
from alveare.views import bid_limit
from alveare.common.database import DB
from alveare.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource

class BidLimitCollection(Resource):
    model = BidLimit
    serializer = bid_limit.serializer
    deserializer = bid_limit.deserializer
    url = '/{}'.format(model.__pluralname__)

    def get(self):
        return get_collection(self.model, self.serializer)
    def post(self):
        return add_to_collection(self.model, self.deserializer, self.serializer)

class BidLimitResource(Resource):
    model = BidLimit
    serializer = bid_limit.serializer
    deserializer = bid_limit.deserializer
    update_deserializer = bid_limit.update_deserializer
    url = '/{}/<int:id>'.format(model.__pluralname__)

    def get(self, id):
        return get_resource(self.model, id, self.serializer)
    def put(self, id):
        return update_resource(self.model, id, self.update_deserializer, self.serializer)
    def delete(self, id):
        return delete_resource(self.model, id)
