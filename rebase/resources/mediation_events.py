from flask.ext.restful import Resource
from flask.ext.login import login_required, current_user
from flask import jsonify, request

from rebase.common.state import ManagedState
from rebase.common.exceptions import NotFoundError
from rebase.common.database import DB
from rebase.models import Mediation
from rebase.views.mediation import (
    serializer,
    initialize_event_deserializer,
    dev_answer_event_deserializer,
    client_answer_event_deserializer,
    timeout_event_deserializer,
    timeout_answer_event_deserializer,
    agree_event_deserializer,
    arbitrate_event_deserializer,
)

class Event(Resource):

    @staticmethod
    def _post(model, view, event_deserializer, *_id):
        instance = model.query.get(_id)
        if not instance:
            raise NotFoundError(model.__tablename__, _id)
        initialize_event = event_deserializer.load(request.form or request.json).data

        with ManagedState():
            instance.machine.send(*initialize_event)

        DB.session.commit()

        response = jsonify({ model.__name__.lower() : view.serializer.dump(instance).data})
        response.status_code = 201
        return response


class MediationInitializeEvents(Event):

    @login_required
    def post(self, id):
        return self._post(serializer, initialize_event_deserializer, id)

        #mediation_instance = Mediation.query.get(id)
        #if not mediation_instance:
            #raise NotFoundError(Mediation.__tablename__, id)
        #initialize_event = mediation_view.initialize_event_deserializer.load(request.form or request.json).data

        #with ManagedState():
            #mediation_instance.machine.send(*initialize_event)

        #DB.session.commit()

        #response = jsonify(mediation = mediation_view.serializer.dump(mediation_instance).data)
        #response.status_code = 201
        #return response

class MediationDevAnswerEvents(Resource):

    @login_required
    def post(self, id):
        mediation_instance = Mediation.query.get(id)
        if not mediation_instance:
            raise NotFoundError(Mediation.__tablename__, id)
        dev_answer_event = mediation_view.dev_answer_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            mediation_instance.machine.send(dev_answer_event)

        DB.session.commit()

        mediation_view.serializer.context = dict(current_user = current_user)
        response = jsonify(mediation_view = mediation_view.serializer.dump(mediation_instance).data)
        response.status_code = 201
        return response

class MediationClientAnswerEvents(Resource):

    @login_required
    def post(self, id):
        mediation_instance = Mediation.query.get(id)
        if not mediation_instance:
            raise NotFoundError(Mediation.__tablename__, id)
        review_event = mediation_view.client_answer_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            mediation_instance.machine.send(review_event)

        DB.session.commit()

        response = jsonify(mediation_view = mediation_view.serializer.dump(mediation_instance).data)
        response.status_code = 201
        return response

class MediationTimeoutEvents(Resource):

    @login_required
    def post(self, id):
        mediation_instance = Mediation.query.get(id)
        if not mediation_instance:
            raise NotFoundError(Mediation.__tablename__, id)
        review_event = mediation_view.timeout_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            mediation_instance.machine.send(review_event)

        DB.session.commit()

        response = jsonify(mediation_view = mediation_view.serializer.dump(mediation_instance).data)
        response.status_code = 201
        return response

class MediationTimeoutAnswerEvents(Resource):

    @login_required
    def post(self, id):
        mediation_instance = Mediation.query.get(id)
        if not mediation_instance:
            raise NotFoundError(Mediation.__tablename__, id)
        review_event = mediation_view.timeout_answer_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            mediation_instance.machine.send(review_event)

        DB.session.commit()

        mediation_view.serializer.context = dict(current_user = current_user)
        response = jsonify(mediation_view = mediation_view.serializer.dump(mediation_instance).data)
        response.status_code = 201
        return response

class MediationAgreeEvents(Resource):

    @login_required
    def post(self, id):
        mediation_instance = Mediation.query.get(id)
        if not mediation_instance:
            raise NotFoundError(Mediation.__tablename__, id)
        review_event = mediation_view.agree_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            mediation_instance.machine.send(review_event)

        DB.session.commit()

        response = jsonify(mediation = mediation_view.serializer.dump(mediation_instance).data)
        response.status_code = 201
        return response

class MediationArbitrateEvents(Resource):

    @login_required
    def post(self, id):
        mediation_instance = Mediation.query.get(id)
        if not mediation_instance:
            raise NotFoundError(Mediation.__tablename__, id)
        review_event = mediation_view.arbitrate_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            mediation_instance.machine.send(review_event)

        DB.session.commit()

        response = jsonify(mediation = mediation_view.serializer.dump(mediation_instance).data)
        response.status_code = 201
        return response
