
from flask.ext.restful import Resource
from marshmallow import fields, Schema
from flask import jsonify, make_response

from alveare.models.organization import Organization
from alveare.views import organization

class OrganizationCollection(Resource):

    def get(self):
        organizations = Organization.query.all()
        response = jsonify(organizations = organization.deserializer.dump(organizations, many=True).data)
        return response
