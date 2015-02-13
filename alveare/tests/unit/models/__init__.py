from .. import AlveareTestCase
from datetime import datetime
from alveare.models import (
    Auction,
    Bid,
    Contractor,
    Ticket,
    TicketSnapshot,
    TicketSet,
    BidLimit,
    TermSheet,
    Work,
    WorkOffer,
    Debit,
    Credit,
    Arbitration,
    Comment,
)

class AlveareModelTestCase(AlveareTestCase):

    def setUp(self):
        '''
        Create mock data in the proper order:
        1/ tickets
        2/ tickets + price + termsheet => auction + ticket_snapshots
        3/ contractor
        4/ auction + contractor + prices  => bid + work offers
        '''
        super().setUp()

        self.ticket_0 = Ticket('Foo','Bar')
        self.ticket_1 = Ticket('Joe', 'Blow')
        self.ticket_2 = Ticket('Yo', 'Mama')
        self.term_sheet = TermSheet('yo mama shall not be so big')
        self.auctionArgs = {
            'ticket_prices':  [ (self.ticket_0, 111), (self.ticket_1, 222), (self.ticket_2, 333) ],
            'term_sheet':     TermSheet('yo mama shall not be so big'),
            'duration':       1000,
            'finish_work_by': datetime.today(),
            'redundancy':     1
        }
        self.auction = Auction(**self.auctionArgs)
        self.contractor = Contractor(100)

        self.db.session.add_all([self.auction, self.contractor])
        self.db.session.commit()

        self.ticket_snapshot_0 = TicketSnapshot.query.filter_by(ticket_id= self.ticket_0.id).first()
        self.ticket_snapshot_1 = TicketSnapshot.query.filter_by(ticket_id= self.ticket_1.id).first()
        self.ticket_snapshot_2 = TicketSnapshot.query.filter_by(ticket_id= self.ticket_2.id).first()

        self.assertNotEqual( self.ticket_snapshot_0, None )
        self.assertNotEqual( self.ticket_snapshot_1, None )
        self.assertNotEqual( self.ticket_snapshot_2, None )

        self.bid = Bid(self.auction, self.contractor)
        # at this point, we have valid:
        #( auction, contractor, bid, ticket_0, ticket_1[..2], tickket_snapshot_0[..2], term_sheet )

    def create_model(self, model, *args, **kwargs):
        instance = model(*args, **kwargs)
        self.db.session.add(instance)
        self.db.session.commit()

        return instance 

    def delete_instance(self, instance):
        self.db.session.delete(instance)
        self.db.session.commit()


    def create_work(self, title, description, work_price=100, rating=None, debit=None, credit=None, mediation_rounds=0):
        work_offer = self.create_work_offer(title, description, work_price)
        work = Work(work_offer)

        if rating != None:
            Review(work, rating)
        if debit != None:
            Debit(work, debit)
        if credit != None:
            Credit(work, credit)
        for mediation_round in range(mediation_rounds):
            Arbitration(Mediation(work))

        self.db.session.add(work)
        return work

    def create_arbitration(self):
        work = self.create_work('dontcare', 'dontcare', 666, mediation_rounds=1)
        return work.mediation_rounds.one().arbitration

    def create_mediation(self):
        work = self.create_work('dontcare', 'dontcare', 666, mediation_rounds=1)
        return work.mediation_rounds.one()

    def create_review(self, rating, comment=None):
        work = self.create_work('dontcare', 'dontcare', 666, rating=rating)
        if comment:
            _ = Comment(work.review, comment)
        return work.review

    def create_debit_and_credit(self, debit_price, credit_price):
        work = self.create_work('dontcare', 'dontcare', 666, debit=debit_price, credit=credit_price)
        return (work.debit, work.credit)

    def create_work_offer(self, ticket_snapshot, work_price):
        work_offer = WorkOffer(self.bid, ticket_snapshot, work_price)
        self.db.session.add(work_offer)
        return work_offer
