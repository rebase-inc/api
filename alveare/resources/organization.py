
from flask.ext.restful import Resource, abort
from marshmallow import fields, Schema
from flask import jsonify, make_response

from alveare.models.organization import Organization
from alveare.views import organization
from alveare.common.database import DB

does_not_exist = 'organization/{}'.format

class OrganizationCollection(Resource):

    def get(self):
        organizations = Organization.query.all()
        response = jsonify(organizations = organization.deserializer.dump(organizations, many=True).data)
        return response

class OrganizationResource(Resource):

    def get(self, id):
        an_organization = Organization.query.get(id)
        if an_organization:
            return jsonify(organization = organization.deserializer.dump(an_organization).data)
        abort(404, message=does_not_exist(id))

    def delete(self, id):
        an_organization = Organization.query.get(id)
        if an_organization:
            DB.session.delete(an_organization)
            DB.session.commit()
            response = jsonify(message = 'Manager succesfully deleted')
            response.status_code = 200
            return response
        abort(404, message=does_not_exist(id))
