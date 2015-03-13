from flask.ext.restful import Resource
from flask import jsonify, make_response, request

from alveare import models
from alveare.views import ticket_snapshot
from alveare.common.database import DB

class TicketSnapshotCollection(Resource):

    def get(self):
        all_snapshots = models.TicketSnapshot.query.limit(100).all()
        response = jsonify(ticket_snapshots = ticket_snapshot.serializer.dump(all_snapshots, many=True).data)
        return response

    def post(self):
        new_ticket_snapshot = ticket_snapshot.deserializer.load(request.form or request.json).data
        DB.session.add(new_ticket_snapshot)
        DB.session.commit()

        response = jsonify(ticket_snapshot = ticket_snapshot.serializer.dump(new_ticket_snapshot).data)
        response.status_code = 201
        return response

class TicketSnapshotResource(Resource):

    def get(self, id):
        single_ticket_snapshot = models.TicketSnapshot.query.get_or_404(id)
        return jsonify(ticket_snapshot = ticket_snapshot.serializer.dump(single_ticket_snapshot).data)

    #def put(self, id):
        #single_ticket_snapshot = models.TicketSnapshot.query.get_or_404(id)

        #for field, value in ticket_snapshot.updater.load(request.form or request.json).data.items():
            #setattr(single_ticket_snapshot, field, value)
        #DB.session.commit()

        #return jsonify(ticket_snapshot = ticket_snapshot.serializer.dump(single_ticket_snapshot).data)

    #def delete(self, id):
        #single_ticket_snapshot = models.TicketSnapshot.query.get(id)
        #DB.session.delete(single_ticket_snapshot)
        #DB.session.commit()
        #response = jsonify(message = 'TicketSnapshot succesfully deleted')
        #response.status_code = 200
        #return response
