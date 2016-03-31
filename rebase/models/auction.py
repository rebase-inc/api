from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask.ext.login import current_app
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

from rebase.common.database import DB, PermissionMixin
from rebase.common.email import Email, send
from rebase.common.exceptions import NoRole, UnknownRole, BadBid
from rebase.common.query import query_from_class_to_user
from rebase.common.state import StateMachine
from rebase.models import BidLimit, Contract, Bid


class Auction(DB.Model, PermissionMixin):
    __pluralname__ = 'auctions'

    id =              DB.Column(DB.Integer,  primary_key=True)
    created =         DB.Column(DB.DateTime, nullable=False)
    expires =         DB.Column(DB.DateTime, nullable=False)
    duration =        DB.Column(DB.Integer,  nullable=False)
    finish_work_by =  DB.Column(DB.DateTime, nullable=False)
    redundancy =      DB.Column(DB.Integer,  nullable=False)
    term_sheet_id =   DB.Column(DB.Integer,  DB.ForeignKey('term_sheet.id', ondelete='CASCADE'), nullable=False)
    state =           DB.Column(DB.String, nullable=False, default='created')

    term_sheet =       DB.relationship('TermSheet',    uselist=False)
    ticket_set =       DB.relationship('TicketSet',    backref='auction', cascade="all, delete-orphan", passive_deletes=True, uselist=False)
    feedbacks =        DB.relationship('Feedback',     backref='auction', cascade='all, delete-orphan', passive_deletes=True)
    bids =             DB.relationship('Bid',          backref='auction', cascade='all, delete-orphan', passive_deletes=True, lazy='dynamic')
    approved_talents = DB.relationship('Nomination',    backref='_auction') # both ends are conditional

    def __init__(self, ticket_set, term_sheet, duration=3, finish_work_by=None, redundancy = 1):
        self.ticket_set = ticket_set
        self.term_sheet = term_sheet
        self.duration = duration
        if not finish_work_by:
            self.finish_work_by = datetime.now() + current_app.config['FINISH_WORK_BY']
        else:
            self.finish_work_by = finish_work_by
        self.redundancy = redundancy
        self.created = datetime.now()
        self.expires = datetime.now() + current_app.config['AUCTION_EXPIRATION']
        # Hack to nominate all contractors during development
        if current_app.config['NOMINATE_ALL_CONTRACTORS']:
            from rebase.models.contractor import Contractor
            from rebase.models.nomination import Nomination
            nominations = [ Nomination(contractor, self.ticket_set) for contractor in Contractor.query.all() ]

    def __repr__(self):
        return '<Auction[id:{}] finish_work_by={}>'.format(self.id, self.finish_work_by)

    @classmethod
    def setup_queries(cls, models):
        cls.as_contractor_path = [
            models.Nomination,
            models.Contractor,
        ]
        cls.as_manager_path = [
            models.TicketSet,
            models.BidLimit,
            models.TicketSnapshot,
            models.Ticket,
            models.Project,
            models.Manager,
        ]
        cls.as_owner_path = [
            models.TicketSet,
            models.BidLimit,
            models.TicketSnapshot,
            models.Ticket,
            models.Project,
            models.Organization,
            models.Owner
        ]

    def allowed_to_be_created_by(self, user):
        return self.ticket_set.bid_limits[0].ticket_snapshot.ticket.allowed_to_be_created_by(user)

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        query_auctions_fn = Auction.role_to_query_fn(user)
        query = query_auctions_fn(user)
        return query.filter(Auction.id==self.id).first()

    @property
    def organization(self):
        return self.ticket_set.bid_limits[0].ticket_snapshot.ticket.organization

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
            raise BadBid(required_tickets, bid_tickets)
        self.auction.bids.append(bid)

        # check to see if overbid or underbid
        for work_offer in bid.work_offers:
            price_limit = BidLimit.query.filter(BidLimit.ticket_snapshot == work_offer.ticket_snapshot).one().price
            if work_offer.price*current_app.config['REVENUE_FACTOR'] > price_limit:
                return

        bid.contract = Contract(bid)
        if self.auction.bids.filter(Bid.contract != None).count() >= self.auction.redundancy:
            send_emails(self.auction, bid)
            self.send('end')

    def failed(self):
        pass

    def ended(self):
        pass

    def __init__(self, auction_instance, initial_state):
        self.auction = auction_instance
        StateMachine.__init__(self, initial_state = getattr(self, initial_state))
        self.add_event_transitions('initialize', {None: self.created})
        self.add_event_transitions('bid', {
            self.created:           self.waiting_for_bids,
            self.waiting_for_bids:  self.waiting_for_bids
        })
        self.add_event_transitions('fail', {
            self.created:           self.failed,
            self.waiting_for_bids:  self.failed
        })
        self.add_event_transitions('end', {
            self.created:           self.ended,
            self.waiting_for_bids:  self.ended,
        })


def send_emails(auction, bid):
    ticket = auction.ticket_set.bid_limits[0].ticket_snapshot.ticket
    contractor = bid.contractor.user
    managers_emails = [ mgr.user.email for mgr in ticket.project.managers ]
    text = '{contractor} won the bid for ticket "{title}" and is now working on it.'.format(
        contractor=contractor.name,
        title=ticket.title
    )
    client_msg = msg(
        'Rebase Auction: match found for ticket "{}"'.format(ticket.title),
        ','.join(managers_emails),
        text,
        text,
    )
    contractor_text = 'You won the bid for the ticket: "{title}"'.format(title=ticket.title)
    contractor_msg = msg(
        'Rebase Auction: you won the bid for ticket "{}"'.format(ticket.title),
        ','.join([contractor.email]),
        contractor_text,
        contractor_text,
    )
    send([
        Email(
            'com.rebaseapp.alpha@rebaseapp.com',
            managers_emails,
            client_msg.as_string()
        ),
        Email(
            'com.rebaseapp.alpha@rebaseapp.com',
            [contractor.email],
            contractor_msg.as_string()
        ),
    ])


def msg(subject, to, plain_text_msg, html_msg):
    _msg = MIMEMultipart('alternative')
    _msg['Subject'] = subject
    _msg['From'] = 'do_not_reply@rebaseapp.com'
    _msg['To'] = to
    html = """\
    <html>
        <head></head>
        <body>
            <p>
            {text}
            </p>
        </body>
    </html>
    """.format(text=plain_text_msg)
    _msg.attach(MIMEText(plain_text_msg, 'plain'))
    _msg.attach(MIMEText(html_msg, 'html'))
    return _msg


