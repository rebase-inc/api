from sqlalchemy.orm import validates

from alveare.common.database import DB
from datetime import datetime

class Auction(DB.Model):

    id =                DB.Column(DB.Integer,   primary_key=True)
    duration =          DB.Column(DB.Integer,   nullable=False)
    finish_work_by =    DB.Column(DB.DateTime,  nullable=False)
    redundancy =        DB.Column(DB.Integer,   nullable=False)
    term_sheet_id =     DB.Column(DB.Integer,   DB.ForeignKey('term_sheet.id'), nullable=False)

    term_sheet =        DB.relationship('TermSheet',    uselist=False)
    ticket_set =        DB.relationship('TicketSet',    backref='auction', cascade="all, delete-orphan", passive_deletes=True, uselist=False)
    feedbacks =         DB.relationship('Feedback',     backref='auction', cascade='all, delete-orphan', passive_deletes=True)
    bids =              DB.relationship('Bid',          backref='auction', cascade='all, delete-orphan', passive_deletes=True)
    approved_talents =  DB.relationship('Candidate',    backref='approved_auction') # both ends are conditional

    def __init__(self, ticket_set, term_sheet, duration, finish_work_by, redundancy = 1):
        self.ticket_set = ticket_set
        self.term_sheet = term_sheet
        self.duration = duration
        self.finish_work_by = finish_work_by
        self.redundancy = redundancy

    def __repr__(self):
        return '<Auction[id:{}] finish_work_by={}>'.format(self.id, self.finish_work_by)

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
