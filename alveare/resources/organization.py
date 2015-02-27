
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

class OrganizationResource(Resource):

    def get(self, id):
        an_organization = Organization.query.get(id)
        return jsonify(organization = organization.deserializer.dump(an_organization).data)
