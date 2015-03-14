
from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare.models.project import Project
from alveare.views.project import serializer, deserializer, update_deserializer
from alveare.common.database import DB


class ProjectCollection(Resource):

    def get(self):
        projects = Project.query.all()
        response = jsonify(projects = serializer.dump(projects, many=True).data)
        return response

    def post(self):
        new_account = deserializer.load(request.form or request.json).data

        DB.session.add(new_account)
        DB.session.commit()

        response = jsonify(project=serializer.dump(new_account).data)
        response.status_code = 201
        return response


class ProjectResource(Resource):

    def get(self, id):
        account = Project.query.get_or_404(id)
        return jsonify(project = serializer.dump(account).data)

    def put(self, id):
        updated_project = update_deserializer.load(request.form or request.json).data

        DB.session.add(updated_project)
        DB.session.commit()

        response = jsonify(project=serializer.dump(updated_project).data)
        response.status_code = 200
        return response

    def delete(self, id):
        DB.session.query(Project).filter_by(id=id).delete()
        DB.session.commit()

        response = jsonify(message = 'Project succesfully deleted')
        response.status_code = 200
        return response
