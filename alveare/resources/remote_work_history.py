
from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare.models.remote_work_history import RemoteWorkHistory
from alveare.views.remote_work_history import serializer, deserializer, update_deserializer
from alveare.common.database import DB


class RemoteWorkHistoryCollection(Resource):

    def get(self):
        remote_work_histories = RemoteWorkHistory.query.all()
        response = jsonify(remote_work_histories = serializer.dump(remote_work_histories, many=True).data)
        return response

    def post(self):
        new_account = deserializer.load(request.form or request.json).data

        DB.session.add(new_account)
        DB.session.commit()

        response = jsonify(remote_work_history=serializer.dump(new_account).data)
        response.status_code = 201
        return response


class RemoteWorkHistoryResource(Resource):

    def get(self, id):
        account = RemoteWorkHistory.query.get_or_404(id)
        return jsonify(remote_work_history = serializer.dump(account).data)

    def put(self, id):
        updated_account = update_deserializer.load(request.form or request.json).data

        DB.session.add(updated_account)
        DB.session.commit()

        response = jsonify(remote_work_history=serializer.dump(updated_account).data)
        response.status_code = 200
        return response

    def delete(self, id):
        DB.session.query(RemoteWorkHistory).filter_by(id=id).delete()
        DB.session.commit()

        response = jsonify(message = 'RemoteWorkHistory succesfully deleted')
        response.status_code = 200
        return response
