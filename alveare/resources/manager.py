
from flask.ext.restful import Resource, abort
from marshmallow import fields, Schema
from flask import jsonify, make_response, request

from alveare.models.manager import Manager
from alveare.models.user import User
from alveare.models.organization import Organization
from alveare.views.manager import serializer, deserializer
from alveare.common.database import DB


class ManagerCollection(Resource):

    def get(self):
        managers = Manager.query.all()
        response = jsonify(managers = serializer.dump(managers, many=True).data)
        return response

    def post(self):
        new_mgr_form = deserializer.load(request.json).data
        user = User.query.get(new_mgr_form['id'])
        organization = Organization.query.get(new_mgr_form['organization_id'])

        new_mgr = Manager(user, organization)
        DB.session.add(new_mgr)
        DB.session.commit()

        response = jsonify(manager = serializer.dump(new_mgr).data)
        response.status_code = 201
        return response

class ManagerResource(Resource):

    def get(self, id):
        single_manager = Manager.query.get(id)
        if single_manager:
            return jsonify(manager = serializer.dump(single_manager).data)
        abort(404, message='manager/{} does not exit'.format(id))

    def delete(self, id):
        DB.session.query(Manager).filter_by(id=id).delete()
        DB.session.commit()

        response = jsonify(message = 'Manager succesfully deleted')
        response.status_code = 200
        return response
