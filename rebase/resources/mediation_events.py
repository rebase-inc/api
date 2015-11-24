from flask.ext.restful import Resource
from flask.ext.login import login_required, current_user
from flask import jsonify, request

from rebase.common.state import ManagedState
from rebase.common.exceptions import NotFoundError
from rebase.common.database import DB
from rebase.models import Mediation
from rebase.views.mediation import (
    serializer,
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
        instance = model.query.get_or_404(_id)
        initialize_event = event_deserializer.load(request.form or request.json).data

        with ManagedState():
            instance.machine.send(*initialize_event)

        DB.session.commit()

        response = jsonify({ model.__name__.lower() : view.serializer.dump(instance).data})
        response.status_code = 201
        return response


#class MediationDevAnswerEvents(Event):

    #@login_required
    #def post(self, id):
        #return self._post(serializer, dev_answer_event_deserializer, id)

        #mediation_instance = Mediation.query.get_or_404(id)
        #dev_answer_event = dev_answer_event_deserializer.load(request.form or request.json).data

        #with ManagedState():
            #mediation_instance.machine.send(*dev_answer_event)

        #DB.session.commit()

        #response = jsonify(mediation = serializer.dump(mediation_instance).data)
        #response.status_code = 201
        #return response

class MediationDevAnswerEvents(Resource):

    @login_required
    def post(self, id):
        mediation_instance = Mediation.query.get_or_404(id)
        dev_answer_event = dev_answer_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            mediation_instance.machine.send(*dev_answer_event)

        DB.session.commit()

        serializer.context = dict(current_user = current_user)
        response = jsonify(mediation = serializer.dump(mediation_instance).data)
        response.status_code = 201
        return response

class MediationClientAnswerEvents(Resource):

    @login_required
    def post(self, id):
        mediation_instance = Mediation.query.get_or_404(id)
        client_answer_event = client_answer_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            mediation_instance.machine.send(*client_answer_event)

        DB.session.commit()

        response = jsonify(mediation = serializer.dump(mediation_instance).data)
        response.status_code = 201
        return response

class MediationTimeoutEvents(Resource):

    @login_required
    def post(self, id):
        mediation_instance = Mediation.query.get_or_404(id)
        review_event = timeout_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            mediation_instance.machine.send(review_event)

        DB.session.commit()

        response = jsonify(mediation = serializer.dump(mediation_instance).data)
        response.status_code = 201
        return response

class MediationTimeoutAnswerEvents(Resource):

    @login_required
    def post(self, id):
        mediation_instance = Mediation.query.get_or_404(id)
        review_event = timeout_answer_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            mediation_instance.machine.send(review_event)

        DB.session.commit()

        serializer.context = dict(current_user = current_user)
        response = jsonify(mediation = serializer.dump(mediation_instance).data)
        response.status_code = 201
        return response

class MediationAgreeEvents(Resource):

    @login_required
    def post(self, id):
        mediation_instance = Mediation.query.get_or_404(id)
        agree_event = agree_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            mediation_instance.machine.send(agree_event)

        DB.session.commit()

        serializer.context = dict(current_user = current_user)
        response = jsonify(mediation = serializer.dump(mediation_instance).data)
        response.status_code = 201
        return response

class MediationArbitrateEvents(Resource):

    @login_required
    def post(self, id):
        mediation_instance = Mediation.query.get_or_404(id)
        arbitrate_event = arbitrate_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            mediation_instance.machine.send(arbitrate_event)

        DB.session.commit()

        serializer.context = dict(current_user = current_user)
        response = jsonify(mediation = serializer.dump(mediation_instance).data)
        response.status_code = 201
        return response
