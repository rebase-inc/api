from marshmallow import fields, Schema

from alveare.views.ticket_set import TicketSetSchema

class AuctionSchema(Schema):
    id =               fields.Integer()
    duration =         fields.Integer()
    finish_work_by =   fields.DateTime()
    redundancy =       fields.Integer()
    #term_sheet =      fields.Nested('TermSheetSchema', only='id')
    ticket_set =       fields.Nested(TicketSetSchema, exclude=('auction',))
    #feedbacks =       fields.Nested('FeedbackSchema', only='id')
    bids =             fields.Nested('BidSchema', only=('id', 'contractor', 'work_offers'), many=True)
    #approved_talents = fields.Nested('CandidateSchema', only='id')

    def make_object(self, data):
        from alveare.models import Auction
        if data.get('id'):
            auction = Auction.query.get(data.get('id'))
            if not auction:
                raise ValueError('No auction with id {id}'.format(**data))
            return auction
        return Auction(**data)

serializer = AuctionSchema(only=('id', 'duration', 'finish_work_by', 'ticket_set', 'bids'), skip_missing=True)
deserializer = AuctionSchema(only=('duration', 'finish_work_by', 'redundancy', 'ticket_set'), strict=True)
