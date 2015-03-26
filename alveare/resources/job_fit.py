
from flask.ext.restful import Resource
from flask.ext.login import login_required, current_user
from flask import jsonify, make_response, request

from alveare.models import JobFit
from alveare.views import job_fit
from alveare.common.database import DB
from alveare.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource
from alveare.common.utils import collection_url, resource_url

class JobFitCollection(Resource):
    model = JobFit
    serializer = job_fit.serializer
    deserializer = job_fit.deserializer
    url = collection_url(model)


    @login_required
    def get(self):
        return get_collection(self.model, self.serializer)

    @login_required
    def post(self):
        return add_to_collection(self.model, self.deserializer, self.serializer)

class JobFitResource(Resource):
    model = JobFit
    serializer = job_fit.serializer
    deserializer = job_fit.deserializer
    update_deserializer = job_fit.update_deserializer
    url = resource_url(model, use_flask_format=True)

    @login_required
    def get(self, contractor_id, ticket_set_id):
        return get_resource(self.model, (contractor_id, ticket_set_id), self.serializer)

    @login_required
    def put(self, contractor_id, ticket_set_id):
        return update_resource(self.model, (contractor_id, ticket_set_id), self.update_deserializer, self.serializer)

    @login_required
    def delete(self, contractor_id, ticket_set_id):
        return delete_resource(self.model, (contractor_id, ticket_set_id))
