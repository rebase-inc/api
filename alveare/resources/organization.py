
from flask.ext.restful import Resource, abort
from marshmallow import fields, Schema
from flask import jsonify, make_response, request

from alveare.models.organization import Organization
from alveare.views import organization
from alveare.common.database import DB

class OrganizationCollection(Resource):

    def get(self):
        organizations = Organization.query.all()
        #raise Exception(organizations)
        response = jsonify(organizations = organization.serializer.dump(organizations, many=True).data)
        return response

    def post(self):
        new_org = organization.deserializer.load(request.form or request.json).data

        DB.session.add(new_org)
        DB.session.commit()

        response = jsonify(organization=organization.serializer.dump(new_org).data)
        response.status_code = 201
        return response


class OrganizationResource(Resource):

    def get(self, id):
        an_organization = Organization.query.get_or_404(id)
        return jsonify(organization = organization.serializer.dump(an_organization).data)

    def put(self, id):
        single_organization = Organization.query.get_or_404(id)

        for field, value in organization.updater.load(request.form or request.json).data.items():
            setattr(single_organization, field, value)
        DB.session.commit()

        DB.session.add(single_organization)
        DB.session.commit()

        response = jsonify(organization=organization.serializer.dump(single_organization).data)
        response.status_code = 200
        return response


    def delete(self, id):
        an_organization = Organization.query.get_or_404(id)
        DB.session.delete(an_organization)
        DB.session.commit()
        response = jsonify(message = 'Organization succesfully deleted')
        response.status_code = 200
        return response
