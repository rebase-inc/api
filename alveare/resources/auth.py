
from flask.ext.restful import Resource
from flask.ext.login import (
    login_required,
    login_user,
    logout_user,
    current_app
)
from flask import jsonify, make_response, request
from alveare.common.exceptions import UnmarshallingError

from alveare.views import auth
from alveare.common.database import DB
from alveare.common.rest import (
    get_collection,
    add_to_collection,
    get_resource,
    update_resource,
    delete_resource
)

class AuthCollection(Resource):
    url = '/auth'

    # TODO: Refactor this to look like other REST endpoints
    def post(self):
        try:
            auth_data = auth.deserializer.load(request.form or request.json).data
            user = auth_data['user']
            password = auth_data['password']
            if not user.check_password(password):
                logout_user()
                response = jsonify(message = 'Incorrect password!')
                response.status_code = 401
                return response
            else:
                login_user(user)
                response = jsonify(message = '{} {} succesfully logged in'.format(user.first_name, user.last_name))
                response.status_code = 201
                return response
        except UnmarshallingError as e:
            logout_user()
            response = jsonify(message = 'No credentials provided!')
            response.status_code = 401
            return response

    @login_required
    def get(self):
        ''' logout '''
        logout_user()
        response = jsonify(message = 'Logged out')
        response.status_code = 200
        return response

