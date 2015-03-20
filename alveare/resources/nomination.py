
from flask.ext.restful import Resource
from flask.ext.login import login_required, current_user
from flask import jsonify, make_response, request

from alveare.models import Nomination
from alveare.views import nomination
from alveare.common.database import DB
from alveare.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource
from alveare.common.utils import collection_url, resource_url

class NominationCollection(Resource):
    model = Nomination
    serializer = nomination.serializer
    deserializer = nomination.deserializer
    url = collection_url(model)

    @login_required
    def get(self):
        return get_collection(self.model, self.serializer, current_user.nomination_query)

    @login_required
    def post(self):
        return add_to_collection(self.model, self.deserializer, self.serializer)

class NominationResource(Resource):
    model = Nomination
    serializer = nomination.serializer
    deserializer = nomination.deserializer
    update_deserializer = nomination.update_deserializer
    url = resource_url(model)

    @login_required
    def get(self, contractor_id, ticket_set_id):
        '''
        You can get a nomination if you're a manager for the organization which owns the ticket_set.
        Contractors can never see a nomination...there is no reason why they would want to.
        '''
        return get_resource(self.model, (contractor_id, ticket_set_id), self.serializer)

    @login_required
    def put(self, contractor_id, ticket_set_id):
        return update_resource(self.model, (contractor_id, ticket_set_id), self.update_deserializer, self.serializer)

    @login_required
    def delete(self, contractor_id, ticket_set_id):
        return delete_resource(self.model, (contractor_id, ticket_set_id))
