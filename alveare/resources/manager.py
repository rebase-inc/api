
from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare.models.manager import Manager
from alveare.views.manager import serializer, deserializer
from alveare.common.database import DB


class ManagerCollection(Resource):

    def get(self):
        managers = Manager.query.all()
        response = jsonify(managers = serializer.dump(managers, many=True).data)
        return response

    def post(self):
        new_mgr = deserializer.load(request.json).data
        DB.session.add(new_mgr)
        DB.session.commit()

        response = jsonify(manager = serializer.dump(new_mgr).data)
        response.status_code = 201
        return response

class ManagerResource(Resource):

    def get(self, id):
        single_manager = Manager.query.get_or_404(id)
        return jsonify(manager = serializer.dump(single_manager).data)

    def delete(self, id):
        DB.session.query(Manager).filter_by(id=id).delete()
        DB.session.commit()

        response = jsonify(message = 'Manager succesfully deleted')
        response.status_code = 200
        return response
