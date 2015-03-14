from marshmallow import fields, Schema

from alveare.views.ticket_set import TicketSetSchema
from alveare.views.term_sheet import TermSheetSchema

class AuctionSchema(Schema):
    id =               fields.Integer()
    duration =         fields.Integer()
    finish_work_by =   fields.DateTime()
    redundancy =       fields.Integer()
    term_sheet =       fields.Nested('TermSheetSchema', exclude=('auction',), required=True)
    ticket_set =       fields.Nested(TicketSetSchema, exclude=('auction',), required=True)
    state =            fields.String()
    #feedbacks =       fields.Nested('FeedbackSchema', only='id')
    bids =             fields.Nested('BidSchema', exclude=('auction',), many=True)
    #approved_talents = fields.Nested('CandidateSchema', only='id')

    def make_object(self, data):
        from alveare.models import Auction
        if data.get('id'):
            auction = Auction.query.get(data.get('id'))
            if not auction:
                raise ValueError('No auction with id {id}'.format(**data))
            return auction
        return Auction(**data)

class BidEventSchema(Schema):
    bid = fields.Nested('BidSchema')

    def make_object(self, data):
        return 'bid', data.pop('bid')

class EndEventSchema(Schema):

    def make_object(self, data):
        return 'end'

class FailEventSchema(Schema):

    def make_object(self, data):
        return 'fail'

serializer = AuctionSchema(only=('id', 'duration', 'finish_work_by', 'ticket_set', 'bids', 'term_sheet', 'redundancy', 'state'), skip_missing=True)
deserializer = AuctionSchema(only=('duration', 'finish_work_by', 'redundancy', 'ticket_set', 'term_sheet'), strict=True)

bid_event_deserializer = BidEventSchema()
end_event_deserializer = EndEventSchema()
fail_event_deserializer = FailEventSchema()
