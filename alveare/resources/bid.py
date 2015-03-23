from flask.ext.login import login_required, current_user
from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare.models import Bid
from alveare.views import bid
from alveare.common.database import DB
from alveare.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource

class BidCollection(Resource):
    model = Bid
    serializer = bid.serializer
    deserializer = bid.deserializer
    url = '/{}'.format(model.__pluralname__)

    @login_required
    def get(self):
        return get_collection(self.model, self.serializer, current_user.bid_query)

    @login_required
    def post(self):
        return add_to_collection(self.model, self.deserializer, self.serializer)

class BidResource(Resource):
    model = Bid
    serializer = bid.serializer
    deserializer = bid.deserializer
    update_deserializer = bid.update_deserializer
    url = '/{}/<int:id>'.format(model.__tablename__)

    @login_required
    def get(self, id):
        return get_resource(self.model, id, self.serializer)

    @login_required
    def put(self, id):
        return update_resource(self.model, id, self.deserializer, self.serializer)

    @login_required
    def delete(self, id):
        return delete_resource(self.model, id)
