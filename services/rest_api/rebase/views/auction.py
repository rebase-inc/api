from os.path import join

from flask import current_app
from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.views.ticket_set import TicketSetSchema
from rebase.views.term_sheet import TermSheetSchema
from rebase.views.nomination import NominationSchema

class AuctionSchema(RebaseSchema):
    id =                fields.Integer()
    created =           fields.DateTime()
    expires =           fields.DateTime()
    duration =          fields.Integer()
    finish_work_by =    fields.DateTime()
    redundancy =        fields.Integer()
    state =             fields.String()
    term_sheet =        SecureNestedField('TermSheetSchema', exclude=('auction',), required=True)
    ticket_set =        SecureNestedField('TicketSetSchema', exclude=('auction',), required=True)
    feedbacks =         SecureNestedField('FeedbackSchema', only='id', many=True)
    bids =              SecureNestedField('BidSchema', only=('id','contractor', 'contract', 'work_offers', 'auction'), many=True)
    organization =      SecureNestedField('OrganizationSchema', only=('id',), required=True)
    approved_talents =  SecureNestedField('NominationSchema', only=('contractor', 'job_fit'), many=True)
    work =              SecureNestedField('WorkSchema', only=('id', 'clone'),  required=False)

    @post_load
    def make_auction(self, data):
        from rebase.models import Auction
        return self._get_or_make_object(Auction, data)


class BidEventSchema(RebaseSchema):

    bid = SecureNestedField('BidSchema', required=True, strict=True)

    @post_load
    def make_bid(self, data):
        return 'bid', data


class EndEventSchema(RebaseSchema):

    @post_load
    def make_end(self, data):
        return 'end', data


class FailEventSchema(RebaseSchema):

    @post_load
    def make_fail(self, data):
        return 'fail', data


serializer = AuctionSchema()
deserializer = AuctionSchema(only=('duration', 'finish_work_by', 'redundancy', 'ticket_set', 'term_sheet', 'approved_talents'), strict=True)
deserializer.declared_fields['term_sheet'].only = None
deserializer.declared_fields['ticket_set'].only = None

update_deserializer = AuctionSchema(only=('id', 'duration', 'term_sheet', 'redundancy', 'approved_talents'), context={'raw': True}, strict=True)

bid_event_deserializer = BidEventSchema(only=('bid',), strict=True)
end_event_deserializer = EndEventSchema()
fail_event_deserializer = FailEventSchema()


