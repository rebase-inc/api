
from flask.ext.restful import Resource, abort
from marshmallow import fields, Schema
from flask import jsonify, make_response, request
from alveare.models.github_project import GithubProject
from alveare.views.github_project import deserializer, serializer
from alveare.common.database import DB

class GithubProjectCollection(Resource):

    def get(self):
        projects = GithubProject.query.all()
        response = jsonify(github_projects = serializer.dump(projects, many=True).data)
        return response

    def post(self):
        new_project = deserializer.load(request.form or request.json).data

        DB.session.add(new_project)
        DB.session.commit()

        response = jsonify(github_project=serializer.dump(new_project).data)
        response.status_code = 201
        return response

class GithubProjectResource(Resource):

    def get(self, id):
        project = GithubProject.query.get_or_404(id)
        return jsonify(github_project = serializer.dump(project).data)

