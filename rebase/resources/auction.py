from flask import current_app
from flask.ext.restful import Resource
from flask.ext.login import login_required, current_user
from flask import jsonify, make_response, request

from rebase.common.database import DB
from rebase.common.rest import get_collection, add_to_collection, get_resource, update_resource, delete_resource
from rebase.common.state import ManagedState
from rebase.models import Auction, Role
from rebase.views import auction as auction_views


@current_app.cache_in_redis.memoize(timeout=3600)
def get_all_auctions(role_id):
    return get_collection(Auction, auction_views.serializer, role_id)


def clear_cache(role_id):
    current_app.cache_in_redis.delete_memoized(get_all_auctions, Auction, auction_views.serializer, role_id)


setattr(get_all_auctions, 'clear_cache', clear_cache)


class AuctionCollection(Resource):
    model = Auction
    serializer = auction_views.serializer
    deserializer = auction_views.deserializer
    url = '/{}'.format(model.__pluralname__)

    @login_required
    def get(self):
        return get_all_auctions(current_user.current_role.id)

    @login_required
    def post(self):
        return add_to_collection(self.model, self.deserializer, self.serializer)


class AuctionResource(Resource):
    model = Auction
    serializer = auction_views.serializer
    deserializer = auction_views.deserializer
    update_deserializer = auction_views.update_deserializer
    url = '/{}/<int:id>'.format(model.__pluralname__)

    @login_required
    def get(self, id):
        return get_resource(self.model, id, self.serializer)

    @login_required
    def put(self, id):
        return update_resource(self.model, id, self.update_deserializer, self.serializer)

    @login_required
    def delete(self, id):
        return delete_resource(self.model, id)


class AuctionBidEvents(Resource):

    @login_required
    def post(self, id):
        single_auction = Auction.query.get_or_404(id)
        auction_event = auction_views.bid_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            single_auction.machine.send(*auction_event)

        DB.session.commit()

        response = jsonify(auction = auction_views.serializer.dump(single_auction).data)
        response.status_code = 201
        return response


class AuctionEndEvents(Resource):

    @login_required
    def post(self, id):
        single_auction = Auction.query.get_or_404(id)
        auction_event = auction_views.end_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            single_auction.machine.send(auction_event)

        DB.session.commit()

        response = jsonify(auction = auction_views.serializer.dump(single_auction).data)
        response.status_code = 201
        return response


class AuctionFailEvents(Resource):

    @login_required
    def post(self, id):
        single_auction = Auction.query.get_or_404(id)
        auction_event = auction_views.fail_event_deserializer.load(request.form or request.json).data

        with ManagedState():
            single_auction.machine.send(auction_event)

        DB.session.commit()

        response = jsonify(auction = auction_views.serializer.dump(single_auction).data)
        response.status_code = 201
        return response
