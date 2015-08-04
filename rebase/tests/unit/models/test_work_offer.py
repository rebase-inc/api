from . import RebaseModelTestCase

from rebase import models
from rebase.common import mock

class TestWorkOfferModel(RebaseModelTestCase):

    def test_delete_bid(self):
        contractor = mock.create_one_contractor(self.db)
        auction = mock.create_one_auction(self.db, redundancy=2)
        self.db.session.commit()

        bid_limits = auction.ticket_set.bid_limits

        work_offers = []
        work_offer_ids = []
        for bid_limit in bid_limits:
            work_offers.append(models.WorkOffer(contractor, bid_limit.ticket_snapshot, int(bid_limit.price * 1.2)))
        bid = models.Bid(auction, contractor)
        self.db.session.add(bid)
        self.db.session.commit()

        work_offer_ids = [wo.id for wo in work_offers]
        self.db.session.delete(bid)
        self.db.session.commit()

        for work_offer_id in work_offer_ids:
            self.assertNotEqual(models.WorkOffer.query.get(work_offer_id), None)

    def test_delete(self):
        contractor = mock.create_one_contractor(self.db)
        auction = mock.create_one_auction(self.db, redundancy=2)
        self.db.session.commit()

        bid_limits = auction.ticket_set.bid_limits

        work_offers = []
        work_offer_ids = []
        for bid_limit in bid_limits:
            work_offers.append(models.WorkOffer(contractor, bid_limit.ticket_snapshot, int(bid_limit.price * 1.2)))
        bid = models.Bid(auction, contractor)
        self.db.session.add(bid)
        self.db.session.commit()

        bid_id = bid.id
        self.assertNotEqual(models.Bid.query.get(bid_id), None)

        self.db.session.delete(work_offers[0])
        self.db.session.delete(work_offers[1])
        self.db.session.commit()

        self.assertEqual(models.Bid.query.get(bid_id), None)
