from datetime import datetime, timedelta
from logging import getLogger
from uuid import uuid1

from flask import jsonify, session, current_app
from flask_restful import Resource
from flask_login import login_user, current_user

from rebase.common.database import DB
from rebase.models import User, Contractor
from rebase.views import user


logger = getLogger(__name__)

# TODO: Remove
class C2RAuthCollection(Resource):
    url = '/c2r_auth'
    bad_credentials = 'Invalid credentials!'

    def get(self):
        if current_user.is_authenticated:
            return jsonify(**{'user': user.serializer.dump(current_user).data})
        else:
            response = jsonify(message=self.bad_credentials)
            response.status_code = 401
            return response

