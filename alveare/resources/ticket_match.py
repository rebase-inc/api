
from flask.ext.restful import Resource
from flask import jsonify, make_response, request
from alveare.common.database import DB
from alveare.models.ticket_match import TicketMatch
from alveare.views.ticket_match import serializer, update_deserializer, deserializer

class TicketMatchCollection(Resource):

    def get(self):
        all_ticket_matches = TicketMatch.query.all()
        response = jsonify(ticket_matches= serializer.dump(all_ticket_matches, many=True).data )
        return response

    def post(self):
        new_ticket_match = deserializer.load(request.form or request.json).data

        DB.session.add(new_ticket_match)
        DB.session.commit()

        response = jsonify(ticket_match= serializer.dump(new_ticket_match).data)
        response.status_code = 201
        return response


class TicketMatchResource(Resource):

    def get(self, skill_requirement_id, skill_set_id):
        a_ticket_match = TicketMatch.query.get_or_404((skill_requirement_id, skill_set_id))
        return jsonify(ticket_match= serializer.dump(a_ticket_match).data)

    def put(self, skill_requirement_id, skill_set_id):
        updated_ticket_match = update_deserializer.load(request.form or request.json).data

        DB.session.add(updated_ticket_match)
        DB.session.commit()

        response = jsonify(ticket_match= serializer.dump(updated_ticket_match).data)
        response.status_code = 200
        return response

    def delete(self, skill_requirement_id, skill_set_id):
        DB.session.query(TicketMatch).filter_by(skill_requirement_id=skill_requirement_id, skill_set_id=skill_set_id).delete()
        DB.session.commit()

        response = jsonify(message = '{} succesfully deleted'.format(TicketMatch.__name__))
        response.status_code = 200
        return response
