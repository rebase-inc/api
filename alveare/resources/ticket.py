
from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare.models.ticket import Ticket
from alveare.views.ticket import serializer, deserializer, update_deserializer
from alveare.common.database import DB


class TicketCollection(Resource):

    def get(self):
        tickets = Ticket.query.all()
        response = jsonify(tickets = serializer.dump(tickets, many=True).data)
        return response

    def post(self):
        new_ticket = deserializer.load(request.form or request.json).data

        DB.session.add(new_ticket)
        DB.session.commit()

        response = jsonify(ticket=serializer.dump(new_ticket).data)
        response.status_code = 201
        return response


class TicketResource(Resource):

    def get(self, id):
        ticket = Ticket.query.get_or_404(id)
        return jsonify(ticket = serializer.dump(ticket).data)

    def put(self, id):
        updated_ticket = update_deserializer.load(request.form or request.json).data

        DB.session.add(updated_ticket)
        DB.session.commit()

        response = jsonify(ticket=serializer.dump(updated_ticket).data)
        response.status_code = 200
        return response

    def delete(self, id):
        DB.session.query(Ticket).filter_by(id=id).delete()
        DB.session.commit()

        response = jsonify(message = 'Ticket succesfully deleted')
        response.status_code = 200
        return response
