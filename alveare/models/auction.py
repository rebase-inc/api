from datetime import datetime, timedelta

from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

from alveare.common.database import DB
from alveare.common.state import StateMachine
from alveare.models import BidLimit, Contract, Bid

class Auction(DB.Model):
    __pluralname__ = 'auctions'

    id =              DB.Column(DB.Integer,   primary_key=True)
    duration =        DB.Column(DB.Integer,   nullable=False)
    finish_work_by =  DB.Column(DB.DateTime,  nullable=False)
    redundancy =      DB.Column(DB.Integer,   nullable=False)
    term_sheet_id =   DB.Column(DB.Integer,   DB.ForeignKey('term_sheet.id', ondelete='CASCADE'), nullable=False)
    state =           DB.Column(DB.String, nullable=False, default='created')
    organization_id = DB.Column(DB.Integer,   DB.ForeignKey('organization.id', ondelete='CASCADE'), nullable=False)

    term_sheet =       DB.relationship('TermSheet',    uselist=False)
    ticket_set =       DB.relationship('TicketSet',    backref='auction', cascade="all, delete-orphan", passive_deletes=True, uselist=False)
    feedbacks =        DB.relationship('Feedback',     backref='auction', cascade='all, delete-orphan', passive_deletes=True)
    bids =             DB.relationship('Bid',          backref='auction', cascade='all, delete-orphan', passive_deletes=True, lazy='dynamic')
    approved_talents = DB.relationship('Nomination',    backref='approved_for_auction') # both ends are conditional

    def __init__(self, organization, ticket_set, term_sheet, duration=3, finish_work_by=datetime.now() + timedelta(days = 7), redundancy = 1):
        self.ticket_set = ticket_set
        self.term_sheet = term_sheet
        self.duration = duration
        self.finish_work_by = finish_work_by
        self.redundancy = redundancy

        self.organization = organization 

    def __repr__(self):
        return '<Auction[id:{}] finish_work_by={}>'.format(self.id, self.finish_work_by)

    @hybrid_property
    def machine(self):
        if hasattr(self, '_machine'):
            return self._machine
        self._machine = AuctionStateMachine(self, initial_state=self.state)
        return self._machine

    @validates('duration', 'redundancy')
    def validate_duration(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        return value

    @validates('finish_work_by')
    def validate_finish_work_by(self, field, value):
        if not isinstance(value, datetime):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, datetime))
        return value

class AuctionStateMachine(StateMachine):

    def set_state(self, old_state, new_state):
        self.auction.state = new_state.__name__

    def created(self):
        pass

    def waiting_for_bids(self, bid):
        required_tickets = set([bid_limit.ticket_snapshot for bid_limit in self.auction.ticket_set.bid_limits])
        bid_tickets = set([work_offer.ticket_snapshot for work_offer in bid.work_offers.all()])
        if required_tickets ^ bid_tickets:
            raise Exception('bid didnt match expected tickets! we needed {} but got {}'.format(required_tickets, bid_tickets))
        self.auction.bids.append(bid)

        # check to see if overbid or underbid
        for work_offer in bid.work_offers:
            price_limit = BidLimit.query.filter(BidLimit.ticket_snapshot == work_offer.ticket_snapshot).one().price
            if work_offer.price > price_limit:
                return

        bid.contract = Contract(bid)
        if self.auction.bids.filter(Bid.contract != None).count() >= self.auction.redundancy:
            self.send('end')

    def failed(self):
        pass

    def ended(self):
        pass

    def __init__(self, auction_instance, initial_state):
        self.auction = auction_instance
        StateMachine.__init__(self, initial_state = getattr(self, initial_state))
        self.add_event_transitions('initialize', {None: self.created})
        self.add_event_transitions('bid', {self.created: self.waiting_for_bids, self.waiting_for_bids:self.waiting_for_bids})
        self.add_event_transitions('fail', {self.created:self.failed, self.waiting_for_bids:self.failed})
        self.add_event_transitions('end', {self.waiting_for_bids:self.ended})
