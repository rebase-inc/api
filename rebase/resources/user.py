
from flask_login import login_required, current_user
from flask_restful import Resource
from flask import jsonify, request, session, current_app

from rebase.models import User, Manager
from rebase.views import user
from rebase.cache.rq_jobs import warmup
from rebase.common.database import DB
from rebase.common.rest import (
    get_collection,
    add_to_collection,
    get_resource,
    update_resource,
    delete_resource
)

class UserCollection(Resource):
    model = User
    serializer = user.serializer
    deserializer = user.deserializer
    url = '/{}'.format(model.__pluralname__)

    @login_required
    def get(self):
        return get_collection(self.model, self.serializer, current_user.current_role.id)

    def post(self):
        return add_to_collection(self.model, self.deserializer, self.serializer)

def update_current_role(user):
    if user == current_user:
        new_role_id = str(user.current_role.id)
        old_role_id = session['role_id']
        if old_role_id != new_role_id:
            warmup(user.current_role.id)
        session['role_id'] = new_role_id
    return user

resource_handlers = {
    'pre_serialization': update_current_role,
}

class UserResource(Resource):
    model = User
    serializer = user.serializer
    deserializer = user.deserializer
    update_deserializer = user.update_deserializer
    url = '/{}/<int:id>'.format(model.__pluralname__)

    @login_required
    def get(self, id):
        return get_resource(self.model, id, self.serializer)

    @login_required
    def put(self, id):
        response = update_resource(self.model, id, self.update_deserializer, self.serializer, handlers=resource_handlers)
        response.set_cookie('role_id', session['role_id'], **current_app.config['COOKIE_SECURE_HTTPPONLY'])
        return response

    @login_required
    def delete(self, id):
        return delete_resource(self.model, id)
