from marshmallow import fields
from rebase.common.schema import RebaseSchema

from rebase.views.ticket_set import TicketSetSchema
from rebase.views.term_sheet import TermSheetSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class AuctionSchema(RebaseSchema):
    id =               fields.Integer()
    duration =         fields.Integer()
    finish_work_by =   fields.DateTime()
    redundancy =       fields.Integer()
    state =            fields.String()
    term_sheet =       SecureNestedField('TermSheetSchema', exclude=('auction',), required=True)
    ticket_set =       SecureNestedField(TicketSetSchema, exclude=('auction',), required=True)
    feedbacks =        SecureNestedField('FeedbackSchema', only='id')
    bids =             SecureNestedField('BidSchema', only=('id',), many=True)
    organization =     SecureNestedField('OrganizationSchema', only=('id',), required=True)
    #approved_talents = SecureNestedField('NominationSchema', only='id')

    def make_object(self, data):
        from rebase.models import Auction
        return get_or_make_object(Auction, data)

class BidEventSchema(RebaseSchema):
    bid = SecureNestedField('BidSchema', required=True)
    def make_object(self, data):
        return 'bid', data.pop('bid')

class EndEventSchema(RebaseSchema):
    def make_object(self, data):
        return 'end'

class FailEventSchema(RebaseSchema):
    def make_object(self, data):
        return 'fail'

serializer = AuctionSchema(only=('id', 'duration', 'finish_work_by', 'ticket_set', 'bids', 'term_sheet', 'redundancy', 'state'), skip_missing=True)
deserializer = AuctionSchema(only=('duration', 'finish_work_by', 'redundancy', 'ticket_set', 'term_sheet'), strict=True)
deserializer.declared_fields['term_sheet'].only = None
deserializer.declared_fields['ticket_set'].only = None

update_deserializer = AuctionSchema(only=tuple(), strict=True)
update_deserializer.make_object = lambda data: data

bid_event_deserializer = BidEventSchema(strict=True)
end_event_deserializer = EndEventSchema()
fail_event_deserializer = FailEventSchema()
