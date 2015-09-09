
from flask import jsonify, make_response, request, redirect, session
from flask.ext.restful import Resource
from flask.ext.login import (
    login_required,
    login_user,
    logout_user,
    current_app,
    current_user
)
from rebase.common.exceptions import UnmarshallingError

from rebase.views import auth, user
from rebase.common.database import DB
from rebase.common.rest import (
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
            auth_user = auth_data['user']
            password = auth_data['password']
            role = auth_data.get('role', '')
            if not auth_user.check_password(password):
                logout_user()
                response = jsonify(message = 'Incorrect password!')
                response.status_code = 401
                return response
            else:
                login_user(auth_user, remember=True)
                current_role = current_user.set_role(role)
                session['role'] = current_role.type
                user.serializer.context = dict(current_user = current_user)
                response = jsonify(**{'user': user.serializer.dump(auth_user).data, 'message': 'success!'})
                response.status_code = 201
                return response
        except UnmarshallingError as e:
            logout_user()
            response = jsonify(message = 'No credentials provided!')
            response.status_code = 401
            return response

    def get(self):
        ''' logout '''
        logout_user()
        response = jsonify(message = 'Logged out')
        response.status_code = 200
        return response

