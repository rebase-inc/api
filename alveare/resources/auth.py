
from flask.ext.restful import Resource
from flask.ext.login import login_user, logout_user
from flask import jsonify, make_response, request
from marshmallow.exceptions import UnmarshallingError

from alveare.views import auth
from alveare.common.database import DB
from alveare.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource

class AuthCollection(Resource):
    url = '/auth'

    def post(self):
        auth_data = auth.deserializer.load(request.form or request.json).data
        if 'user' in auth_data:
            authed_user = auth_data.get('user')
            login_user(authed_user)
            response = jsonify(message = '{} succesfully logged in'.format(authed_user.first_name))
            response.status_code = 201
            return response
        else:
            logout_user()
            response = jsonify(message = 'Logged out')
            response.status_code = 201
            return response
