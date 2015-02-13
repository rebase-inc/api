from sqlalchemy.orm import validates

from alveare.common.database import DB
from alveare.models.ticket_set import TicketSet
from alveare.models.term_sheet import TermSheet
from datetime import datetime

class Auction(DB.Model):

    id =                DB.Column(DB.Integer,   primary_key=True)
    duration =          DB.Column(DB.Integer,   nullable=False)
    finish_work_by =    DB.Column(DB.DateTime,  nullable=False)
    redundancy =        DB.Column(DB.Integer,   nullable=False)

    ticket_set =        DB.relationship('TicketSet', backref='auction', uselist=False, cascade="all, delete-orphan")

    term_sheet =        DB.relationship(TermSheet, uselist=False)
    term_sheet_id =     DB.Column(DB.Integer,    DB.ForeignKey('term_sheet.id'), nullable=False)

    def __init__(self, ticket_prices, term_sheet, duration, finish_work_by, redundancy = 1):
        '''
            ticket_prices is a list of (ticket, price)
        '''
        self.duration = duration
        self.finish_work_by = finish_work_by
        self.redundancy = redundancy

        self.term_sheet = term_sheet
        self.ticket_set = TicketSet()
        for ticket, price in ticket_prices:
            self.ticket_set.add(ticket, price)

    def __repr__(self):
        return '<Auction[id:{}] finish_work_by={}>'.format(self.id, self.finish_work_by)

    @validates('duration', 'redundancy')
    def validate_duration(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        return value
