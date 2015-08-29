from flask.ext.restful import Resource
from flask.ext.login import login_required, current_user
from flask import jsonify, make_response, request

from rebase.common.state import ManagedState
from rebase.common.exceptions import NotFoundError
from rebase.common.database import DB
from rebase.models import Work
from rebase.views import work

class WorkHaltEvents(Resource):

    @login_required
    def post(self, id):
        work_instance = Work.query.get(id)
        if not work_instance:
            raise NotFoundError(Work.__tablename__, id)
        halt_event = work.halt_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            work_instance.machine.send(*halt_event)

        DB.session.commit()

        response = jsonify(work = work.serializer.dump(work_instance).data)
        response.status_code = 201
        return response

class WorkReviewEvents(Resource):

    @login_required
    def post(self, id):
        work_instance = Work.query.get(id)
        if not work_instance:
            raise NotFoundError(Work.__tablename__, id)
        review_event = work.review_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            work_instance.machine.send(review_event)

        DB.session.commit()

        work.serializer.context = dict(current_user = current_user)
        response = jsonify(work = work.serializer.dump(work_instance).data)
        response.status_code = 201
        return response

class WorkMediateEvents(Resource):

    @login_required
    def post(self, id):
        work_instance = Work.query.get(id)
        if not work_instance:
            raise NotFoundError(Work.__tablename__, id)
        review_event = work.mediate_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            work_instance.machine.send(review_event)

        DB.session.commit()

        response = jsonify(work = work.serializer.dump(work_instance).data)
        response.status_code = 201
        return response

class WorkCompleteEvents(Resource):

    @login_required
    def post(self, id):
        work_instance = Work.query.get(id)
        if not work_instance:
            raise NotFoundError(Work.__tablename__, id)
        review_event = work.complete_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            work_instance.machine.send(review_event)

        DB.session.commit()

        response = jsonify(work = work.serializer.dump(work_instance).data)
        response.status_code = 201
        return response

class WorkResumeEvents(Resource):

    @login_required
    def post(self, id):
        work_instance = Work.query.get(id)
        if not work_instance:
            raise NotFoundError(Work.__tablename__, id)
        review_event = work.resume_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            work_instance.machine.send(review_event)

        DB.session.commit()

        work.serializer.context = dict(current_user = current_user)
        response = jsonify(work = work.serializer.dump(work_instance).data)
        response.status_code = 201
        return response

class WorkFailEvents(Resource):

    @login_required
    def post(self, id):
        work_instance = Work.query.get(id)
        if not work_instance:
            raise NotFoundError(Work.__tablename__, id)
        review_event = work.fail_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            work_instance.machine.send(review_event)

        DB.session.commit()

        response = jsonify(work = work.serializer.dump(work_instance).data)
        response.status_code = 201
        return response
