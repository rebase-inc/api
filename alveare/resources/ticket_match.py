
from flask.ext.restful import Resource
from flask import jsonify, make_response, request
from alveare.common.database import DB
from alveare.models.ticket_match import TicketMatch
from alveare.views import ticket_match
from alveare.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource

class TicketMatchCollection(Resource):
    model = TicketMatch
    serializer = ticket_match.serializer
    deserializer = ticket_match.deserializer
    url = '/{}'.format(model.__pluralname__)

    def get(self):
        return get_collection(self.model, self.serializer)
    def post(self):
        return add_to_collection(self.model, self.deserializer, self.serializer)

class TicketMatchResource(Resource):
    model = TicketMatch
    serializer = ticket_match.serializer
    deserializer = ticket_match.deserializer
    update_deserializer = ticket_match.update_deserializer
    url = '/{}/<int:skill_requirement_id>/<int:skill_set_id>'.format(model.__pluralname__)

    def get(self, skill_requirement_id, skill_set_id):
        composite_id = (skill_requirement_id, skill_set_id)
        return get_resource(self.model, composite_id, self.serializer)

    def put(self, skill_requirement_id, skill_set_id):
        composite_id = (skill_requirement_id, skill_set_id)
        return update_resource(self.model, composite_id, self.update_deserializer, self.serializer)

    def delete(self, skill_requirement_id, skill_set_id):
        composite_id = (skill_requirement_id, skill_set_id)
        return delete_resource(self.model, composite_id)
