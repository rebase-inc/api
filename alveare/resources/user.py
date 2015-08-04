
from flask.ext.login import login_required, current_user
from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from rebase.models import User, Manager
from rebase.views import user
from rebase.common.database import DB
from rebase.common.rest import (
    query_string_values,
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
        return get_collection(self.model, self.serializer)

    def post(self):
        return add_to_collection(self.model, self.deserializer, self.serializer)

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
        return update_resource(self.model, id, self.update_deserializer, self.serializer)

    @login_required
    def delete(self, id):
        return delete_resource(self.model, id)
