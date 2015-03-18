
from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare.models import Candidate
from alveare.views import candidate
from alveare.common.database import DB
from alveare.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource
from alveare.common.utils import collection_url, resource_url

class CandidateCollection(Resource):
    model = Candidate
    serializer = candidate.serializer
    deserializer = candidate.deserializer
    url = collection_url(model)

    def get(self):
        return get_collection(self.model, self.serializer)
    def post(self):
        return add_to_collection(self.model, self.deserializer, self.serializer)

class CandidateResource(Resource):
    model = Candidate
    serializer = candidate.serializer
    deserializer = candidate.deserializer
    update_deserializer = candidate.update_deserializer
    url = resource_url(model)

    def get(self, contractor_id, ticket_set_id):
        return get_resource(self.model, (contractor_id, ticket_set_id), self.serializer)
    def put(self, contractor_id, ticket_set_id):
        return update_resource(self.model, (contractor_id, ticket_set_id), self.update_deserializer, self.serializer)
    def delete(self, contractor_id, ticket_set_id):
        return delete_resource(self.model, (contractor_id, ticket_set_id))
