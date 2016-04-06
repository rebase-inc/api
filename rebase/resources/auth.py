from datetime import datetime, timedelta

from flask import jsonify, request, session, current_app
from flask.ext.restful import Resource
from flask.ext.login import (
    login_required,
    login_user,
    logout_user,
    current_user,
)

from rebase.cache.rq_jobs import warmup, cooldown
from rebase.common.exceptions import ValidationError
from rebase.views import auth, user


class AuthCollection(Resource):
    url = '/auth'
    bad_credentials = 'Invalid credentials!\nVerify that both the email and the password you entered are correct.'

    # TODO: Refactor this to look like other REST endpoints
    def post(self):
        try:
            auth_data = auth.deserializer.load(request.form or request.json).data
            auth_user = auth_data['user']
            password = auth_data['password']
            role_id = int(request.cookies.get('role_id', 0))
            if not auth_user.check_password(password):
                logout_user()
                response = jsonify(message=self.bad_credentials)
                response.status_code = 401
                return response
            else:
                login_user(auth_user, remember=True)
                current_role = current_user.set_role(role_id)
                session['role_id'] = current_role.id
                user.serializer.context = dict(current_user = current_user)
                response = jsonify(**{
                    'user': user.serializer.dump(auth_user).data,
                    'message': 'success!'
                })
                warmup(current_role.id)
                response.status_code = 201
                response.set_cookie(
                    'role_id',
                    str(current_role.id),
                    expires=datetime.now()+timedelta(days=1),
                    **current_app.config['COOKIE_SECURE_HTTPPONLY']
                )
                return response
        except ValidationError as e:
            logout_user()
            response = jsonify(message=self.bad_credentials)
            response.status_code = 401
            return response

    def get(self):
        if current_user.is_authenticated():
            warmup(current_user.current_role.id)
            return jsonify(**{'user': user.serializer.dump(current_user).data})
        else:
            response = jsonify(message=self.bad_credentials)
            response.status_code = 401
            return response

    def delete(self):
        ''' logout '''
        role_id = int(request.cookies.get('role_id', 0))
        cooldown(role_id)
        logout_user()
        response = jsonify(message = 'Logged out')
        response.status_code = 200
        session.pop('github_token', None)
        return response

