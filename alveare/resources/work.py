
from flask.ext.restful import Resource
from flask.ext.login import login_required, current_user
from flask import jsonify, make_response, request

from alveare import models
from alveare.views import work
from alveare.common.database import DB

class WorkCollection(Resource):

    @login_required
    def get(self):
        all_work = models.Work.query.limit(100).all()
        response = jsonify(work = work.serializer.dump(all_work, many=True).data) #something here is very very slow..TODO: investigate
        return response

class WorkResource(Resource):

    @login_required
    def get(self, id):
        single_work = models.Work.query.get_or_404(id)
        return jsonify(work = work.serializer.dump(single_work).data)

    @login_required
    def put(self, id):
        single_user = models.Work.query.get_or_404(id)

        for field, value in user.updater.load(request.form).data.items():
            setattr(single_user, field, value)
        DB.session.commit()

        return jsonify(users = user.serializer.dump(single_user).data)
