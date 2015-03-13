from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare import models
from alveare.views import ticket_set
from alveare.common.database import DB

class TicketSetCollection(Resource):

    #def get(self):
        #all_ticket_sets = models.TicketSet.query.limit(100).all()
        #response = jsonify(ticket_sets = ticket_set.serializer.dump(all_ticket_sets, many=True).data)
        #return response

    def post(self):
        new_ticket_set = ticket_set.deserializer.load(request.form or request.json).data
        DB.session.add(new_ticket_set)
        DB.session.commit()

        response = jsonify(ticket_set = ticket_set.serializer.dump(new_ticket_set).data)
        response.status_code = 201
        return response

class TicketSetResource(Resource):
    pass
    #def get(self, id):
        #single_ticket_set = models.TicketSet.query.get_or_404(id)
        #return jsonify(ticket_set = ticket_set.serializer.dump(single_ticket_set).data)

    ##def put(self, id):
        ##single_ticket_set = models.TicketSet.query.get_or_404(id)

        ##for field, value in ticket_set.updater.load(request.form or request.json).data.items():
            ##setattr(single_ticket_set, field, value)
        ##DB.session.commit()

        ##return jsonify(ticket_set = ticket_set.serializer.dump(single_ticket_set).data)

    ##def delete(self, id):
        ##single_ticket_set = models.TicketSet.query.get(id)
        ##DB.session.delete(single_ticket_set)
        ##DB.session.commit()
        ##response = jsonify(message = 'TicketSet succesfully deleted')
        ##response.status_code = 200
        ##return response
