
from flask.ext.restful import Resource
from flask.ext.login import login_required, current_user
from flask import jsonify, make_response, request

from alveare.models import Ticket
from alveare.views import ticket
from alveare.common.database import DB
from alveare.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource

class TicketCollection(Resource):
    model = Ticket
    serializer = ticket.serializer
    deserializer = ticket.deserializer
    url = '/{}'.format(model.__pluralname__)

    @login_required
    def get(self):
        return get_collection(self.model, self.serializer)
    @login_required
    def post(self):
        return add_to_collection(self.model, self.deserializer, self.serializer)

class TicketResource(Resource):
    model = Ticket
    serializer = ticket.serializer
    deserializer = ticket.deserializer
    update_deserializer = ticket.update_deserializer
    url = '/{}/<int:id>'.format(model.__pluralname__)

    @login_required
    def get(self, id):
        return get_resource(self.model, id, self.serializer)
    @login_required
    def put(self, id):
        return update_resource(self.model, id, self.update_deserializer, self.serializer)
    @login_required
    def delete(self, id):
        return delete_resource(self.model, id)
