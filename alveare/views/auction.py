from marshmallow import fields
from alveare.common.schema import AlveareSchema

from alveare.views.ticket_set import TicketSetSchema
from alveare.views.term_sheet import TermSheetSchema
from alveare.common.database import get_or_make_object

class AuctionSchema(AlveareSchema):
    id =               fields.Integer()
    duration =         fields.Integer()
    finish_work_by =   fields.DateTime()
    redundancy =       fields.Integer()
    term_sheet =       fields.Nested('TermSheetSchema', exclude=('auction',), required=True)
    ticket_set =       fields.Nested(TicketSetSchema, exclude=('auction',), required=True)
    state =            fields.String()
    #feedbacks =       fields.Nested('FeedbackSchema', only='id')
    bids =             fields.Nested('BidSchema', only=('id',), many=True)
    organization =     fields.Nested('OrganizationSchema', only=('id',), required=True)
    #approved_talents = fields.Nested('NominationSchema', only='id')

    def make_object(self, data):
        from alveare.models import Auction
        return get_or_make_object(Auction, data)

class BidEventSchema(AlveareSchema):
    bid = fields.Nested('BidSchema')
    def make_object(self, data):
        return 'bid', data.pop('bid')

class EndEventSchema(AlveareSchema):
    def make_object(self, data):
        return 'end'

class FailEventSchema(AlveareSchema):
    def make_object(self, data):
        return 'fail'

serializer = AuctionSchema(only=('id', 'duration', 'finish_work_by', 'ticket_set', 'bids', 'term_sheet', 'redundancy', 'state'), skip_missing=True)
deserializer = AuctionSchema(only=('duration', 'finish_work_by', 'redundancy', 'ticket_set', 'term_sheet'), strict=True)
deserializer.declared_fields['term_sheet'].only = None
deserializer.declared_fields['ticket_set'].only = None

update_deserializer = AuctionSchema(only=tuple(), strict=True)
update_deserializer.make_object = lambda data: data

bid_event_deserializer = BidEventSchema()
end_event_deserializer = EndEventSchema()
fail_event_deserializer = FailEventSchema()

