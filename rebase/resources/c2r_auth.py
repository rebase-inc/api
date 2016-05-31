from datetime import datetime, timedelta
from logging import getLogger
from uuid import uuid1

from flask import jsonify, request, session, current_app, _app_ctx_stack
from flask.ext.restful import Resource
from flask.ext.login import login_user, current_user

from rebase.common.database import DB
from rebase.models import User, Contractor
from rebase.views import user


logger = getLogger()


def make_temp_dev_user():
    new_user = User(
        'John Doe',
        uuid1().hex+'@nop.rebaseapp.com',
        ''
    )
    dev = Contractor(new_user)
    DB.session.add(new_user)
    DB.session.commit()
    return new_user, dev.id


class C2RAuthCollection(Resource):
    url = '/c2r_auth'

    def get(self):
        if current_user.is_authenticated:
            return jsonify(**{'user': user.serializer.dump(current_user).data})
        else:
            auth_user, role_id = make_temp_dev_user()
            login_user(auth_user, remember=True)
            current_role = current_user.set_role(role_id)
            session['role_id'] = current_role.id
            user.serializer.context = dict(current_user = current_user)
            response = jsonify(**{
                'user': user.serializer.dump(auth_user).data,
                'message': 'success!'
            })
            response.status_code = 201
            response.set_cookie(
                'role_id',
                str(current_role.id),
                expires=datetime.now()+timedelta(days=1),
                **current_app.config['COOKIE_SECURE_HTTPPONLY']
            )
            return response

