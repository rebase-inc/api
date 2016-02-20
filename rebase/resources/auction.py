from flask import current_app
from flask.ext.restful import Resource
from flask.ext.login import login_required
from flask import jsonify, request

from rebase.cache.rq_jobs import invalidate
from rebase.common.database import DB
from rebase.common.state import ManagedState
from rebase.models import Auction
from rebase.resources import RestfulResource, RestfulCollection
from rebase.views import auction as auction_views


AuctionResource = RestfulResource(
    Auction,
    auction_views.serializer,
    auction_views.deserializer,
    auction_views.update_deserializer,
)


AuctionCollection = RestfulCollection(
    Auction,
    auction_views.serializer,
    auction_views.deserializer,
    cache=True
)


get_all_auctions = AuctionCollection.get_all


class AuctionEvent(Resource):

    @login_required
    def post(self, id):
        single_auction = Auction.query.get_or_404(id)
        auction_event = self.deserializer.load(request.form or request.json).data

        with ManagedState():
            single_auction.machine.send(auction_event)

        DB.session.commit()

        # update the cache
        invalidate([(Auction, id)])

        response = jsonify(auction = auction_views.serializer.dump(single_auction).data)
        response.status_code = 201
        return response


AuctionBidEvents = type('AuctionBidEvents', (AuctionEvent,), dict(deserializer=auction_views.bid_event_deserializer))
AuctionEndEvents = type('AuctionEndEvents', (AuctionEvent,), dict(deserializer=auction_views.end_event_deserializer))
AuctionFailEvents = type('AuctionFailEvents', (AuctionEvent,), dict(deserializer=auction_views.fail_event_deserializer))


