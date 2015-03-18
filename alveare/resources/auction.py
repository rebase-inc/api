
from flask.ext.restful import Resource
from flask.ext.login import login_required, current_user
from flask import jsonify, make_response, request
from sqlalchemy import or_

from marshmallow.exceptions import UnmarshallingError

from alveare.models import Auction, Role
from alveare.views import auction
from alveare.common.database import DB
from alveare.common.state import ManagedState
from alveare.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource

class AuctionCollection(Resource):
    model = Auction
    serializer = auction.serializer
    deserializer = auction.deserializer
    url = '/{}'.format(model.__pluralname__)

    @login_required
    def get(self):
        manager_roles = current_user.roles.filter(Role.type == 'manager').all()
        manager_for_organizations = [manager.organization.id for manager in manager_roles]
        contractor_roles = current_user.roles.filter(Role.type == 'contractor').all()

        auctions_approved_for = []
        for contractor_role in contractor_roles:
            for candidacy in contractor_role.candidates:
                approved = candidacy.approved_for_auction
                if approved: auctions_approved_for.append(approved.id)

        # hacky...maybe we should probably restrict them to using one role at a time
        if current_user.is_admin():
            query_filters = []
        elif auctions_approved_for and manager_for_organizations:
            approved_auction_filter = Auction.id.in_(auctions_approved_for)
            manager_for_filter = Auction.organization_id.in_(manager_for_organizations)
            query_filters = [or_(approved_auction_filter, manager_for_filter)]
        elif auctions_approved_for:
            approved_auction_filter = Auction.id.in_(auctions_approved_for)
            query_filters = [approved_auction_filter]
        elif manager_for_organizations:
            manager_for_filter = Auction.organization_id.in_(manager_for_organizations)
            query_filters = [manager_for_filter]
        else:
            query_filters = [None]
       
        return get_collection(self.model, self.serializer, query_filters)
    
    def post(self):
        return add_to_collection(self.model, self.deserializer, self.serializer)

class AuctionResource(Resource):
    model = Auction
    serializer = auction.serializer
    deserializer = auction.deserializer
    update_deserializer = auction.update_deserializer
    url = '/{}/<int:id>'.format(model.__pluralname__)

    def get(self, id):
        return get_resource(self.model, id, self.serializer)
    def put(self, id):
        return update_resource(self.model, id, self.update_deserializer, self.serializer)
    def delete(self, id):
        return delete_resource(self.model, id)

class AuctionBidEvents(Resource):

    def post(self, id):
        single_auction = Auction.query.get_or_404(id)
        auction_event = auction.bid_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            single_auction.machine.send(auction_event)

        DB.session.commit()

        response = jsonify(auction = auction.serializer.dump(single_auction).data)
        response.status_code = 201
        return response

class AuctionEndEvents(Resource):

    def post(self, id):
        single_auction = Auction.query.get_or_404(id)
        auction_event = auction.end_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            single_auction.machine.send(auction_event)

        DB.session.commit()

        response = jsonify(auction = auction.serializer.dump(single_auction).data)
        response.status_code = 201
        return response

class AuctionFailEvents(Resource):

    def post(self, id):
        single_auction = Auction.query.get_or_404(id)
        auction_event = auction.fail_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            single_auction.machine.send(auction_event)

        DB.session.commit()

        response = jsonify(auction = auction.serializer.dump(single_auction).data)
        response.status_code = 201
        return response
