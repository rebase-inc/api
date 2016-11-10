import datetime

from flask import current_app
from flask.ext.login import current_user
from sqlalchemy.orm import validates, reconstructor
from sqlalchemy.ext.hybrid import hybrid_property

from rebase.models.comment import Comment
from rebase.common.database import DB, PermissionMixin
from rebase.common.email import Email, send
from rebase.common.state import StateMachine


class Work(DB.Model, PermissionMixin):
    __pluralname__ = 'works'

    id =            DB.Column(DB.Integer, primary_key=True)
    state =         DB.Column(DB.String, nullable=False, default='in_progress')
    branch =        DB.Column(DB.String, nullable=False)
    work_offer_id = DB.Column(DB.Integer, DB.ForeignKey('work_offer.id', ondelete='CASCADE'), nullable=False)

    debit =         DB.relationship('Debit',        backref='work', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    credit =        DB.relationship('Credit',       backref='work', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    review =        DB.relationship('Review',       backref='work', lazy='joined', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    mediations =    DB.relationship('Mediation',    backref='work', lazy='joined', cascade='all, delete-orphan', passive_deletes=True, order_by='Mediation.id')
    comments =      DB.relationship('Comment',      backref='work', lazy='joined', cascade='all, delete-orphan', passive_deletes=True, order_by='Comment.created')
    blockages =     DB.relationship('Blockage',     backref='work', lazy='joined', cascade='all, delete-orphan', passive_deletes=True, order_by='Blockage.id')

    _clone = 'git clone -b {branch} --single-branch {url}'

    def __init__(self, work_offer):
        self.offer = work_offer
        self.branch = current_app.config['WORK_BRANCH_NAME'](
            contractor_id=self.offer.contractor_id,
            auction_id=self.offer.bid.auction_id
        )
        project = self.offer.ticket_snapshot.ticket.project
        from rebase.git.repo import Repo
        repo = Repo(project)
        repo.create_branch(self.branch)

    @reconstructor
    def init(self):
        self.clone = Work._clone.format(
            branch=self.branch,
            url=self.offer.ticket_snapshot.ticket.project.work_repo.url
        )

    @classmethod
    def setup_queries(cls, models):
        cls.as_owner_path = [
            models.WorkOffer,
            models.TicketSnapshot,
            models.Ticket,
            models.Project,
            models.Organization,
            models.Owner,
        ]
        cls.as_contractor_path = [
            models.WorkOffer,
            models.Bid,
            models.Contractor,
        ]
        cls.as_manager_path = [
            models.WorkOffer,
            models.TicketSnapshot,
            models.Ticket,
            models.Project,
            models.Manager
        ]

    def allowed_to_be_created_by(self, user):
        return user.is_admin()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        elif self.offer.contractor.user == user:
            return True
        elif self.offer.bid and self.offer.bid.auction.organization.id in user.manager_for_projects:
            return True
        else:
            return False

    @hybrid_property
    def machine(self):
        if hasattr(self, '_machine'):
            return self._machine
        self._machine = WorkStateMachine(self, initial_state=self.state)
        return self._machine

    @validates('offer')
    def validate_work_offer(self, field, value):
        from rebase.models.work_offer import WorkOffer
        if not isinstance(value, WorkOffer):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, WorkOffer))
        return value

    def __repr__(self):
        return '<Work[{}] from Offer[{}]>'.format(self.id, self.offer.id)


class WorkStateMachine(StateMachine):

    def __init__(self, work_instance, initial_state):
        self.work = work_instance
        StateMachine.__init__(self, initial_state = getattr(self, initial_state))
        self.add_event_transitions('halt_work', {self.in_progress: self.blocked})
        self.add_event_transitions('review', {
            self.in_progress: self.in_review,
            self.in_mediation: self.wait_for_rating
        })
        self.add_event_transitions('mediate', {self.in_review: self.in_mediation})
        self.add_event_transitions('complete', {
            self.in_review: self.complete,
            self.in_mediation: self.complete,
            self.wait_for_rating: self.complete
        })
        self.add_event_transitions('resolve', {
            self.in_mediation: self.in_progress,
            self.blocked: self.resolved
        })
        self.add_event_transitions('resume', {self.resolved: self.in_progress })
        self.add_event_transitions('fail', {self.in_mediation: self.failed})

    def set_state(self, _, new_state):
        self.work.state = new_state.__name__

    def in_progress(self, comment=None):
        if comment:
            Comment(current_user, comment, work=self.work)

    def blocked(self, comment):
        from rebase.models.blockage import Blockage
        Blockage(self.work, comment)

    def in_review(self, comment=None):
        if comment:
            Comment(current_user, comment, work=self.work)
        send_in_review_email(self.work)

    def resolved(self, comment):
        Comment(current_user, comment, work=self.work)
        # this ending date is a hack that should be fixed by adding a state machine to the blockage
        if len(self.work.blockages):
            self.work.blockages[-1].ended = datetime.datetime.now()
        self.send('resume')

    def in_mediation(self, comment):
        from rebase.models.mediation import Mediation
        Mediation(self.work, comment)
        send_in_mediation_email(self.work, comment)

    def wait_for_rating(self):
        send_in_review_email(self.work)

    def complete(self, comment, rating):
        from rebase.models import Debit, Credit, Review
        review = Review(self.work, comment)
        review.rating = rating
        DB.session.add(review)
        Debit(self.work, int(self.work.offer.price*current_app.config['REVENUE_FACTOR']))
        Credit(self.work, self.work.offer.price)
        send_complete_email(self.work)

    def failed(self):
        send_in_arbitration_email(self.work)


def send_in_review_email(work):
    ticket = work.offer.ticket_snapshot.ticket
    managers_emails = [ mgr.user.email for mgr in ticket.project.managers ]
    contractor = work.offer.bid.contractor.user
    client_text = 'Waiting for your review on ticket:\n"{title}"'.format(title=ticket.title)
    client_email = Email(
        'do_not_reply@rebaseapp.com',
        managers_emails,
        'Rebase Review: ticket "{}"'.format(ticket.title),
        client_text,
        client_text,
    )
    send([ client_email ])


def send_in_mediation_email(work, comment):
    ticket = work.offer.ticket_snapshot.ticket
    contractor = work.offer.bid.contractor.user
    contractor_text = '''
    The work you did for Ticket:
    "{title}"
    has been reviewed.
    {client} is not ready to mark the work as complete yet.
    {client} commented:
    "{comment}"
    The work is now in a mediation state and you are welcome to 
    discuss it in order to come to an agreement.
    If in the end both sides cannot agree, the work for this ticket will be placed in arbitration.
    '''.format(
        title=ticket.title,
        client=current_user.name,
        comment=comment,
    )
    contractor_email = Email(
        'do_not_reply@rebaseapp.com',
        [ contractor.email ],
        'Rebase Review: ticket "{}"'.format(ticket.title),
        contractor_text,
        contractor_text,
    )
    send([ contractor_email ])


def send_in_arbitration_email(work):
    ticket = work.offer.ticket_snapshot.ticket
    managers_emails = [ mgr.user.email for mgr in ticket.project.managers ]
    contractor = work.offer.bid.contractor.user
    contractor_text = '''
    An independent arbitration has been requested for the work you did for ticket:
    "{title}"
    The work, review and mediation will be assessed and a decision will be provided
    within 5 business days.
    Thank you for your patience.

    The Rebase Team
    '''.format(
        title=ticket.title,
    )
    contractor_email = Email(
        'do_not_reply@rebaseapp.com',
        [ contractor.email ],
        'Rebase Review: ticket "{}"'.format(ticket.title),
        contractor_text,
        contractor_text,
    )
    client_text = '''
    An independent arbitration has been requested for the work you requested for ticket:
    "{title}"
    The work, review and mediation will be assessed and a decision will be provided
    within 5 business days.
    Thank you for your patience.

    The Rebase Team
    '''.format(
        title=ticket.title,
    )
    client_email = Email(
        'do_not_reply@rebaseapp.com',
        managers_emails,
        'Rebase Review: ticket "{}"'.format(ticket.title),
        client_text,
        client_text,
    )
    send([ contractor_email, client_email ])


def send_complete_email(work):
    ticket = work.offer.ticket_snapshot.ticket
    managers_emails = [ mgr.user.email for mgr in ticket.project.managers ]
    contractor = work.offer.bid.contractor.user
    contractor_text = '''
    Congratulations!
    Your work for ticket:
    "{title}"
    has been completed.
    You will be paid ${price}.

    Thank you for hard work!

    The Rebase Team
    '''.format(
        title=ticket.title,
        price=work.credit.price
    )
    contractor_email = Email(
        'do_not_reply@rebaseapp.com',
        [ contractor.email ],
        'Rebase: completed ticket "{}"'.format(ticket.title),
        contractor_text,
        contractor_text,
    )
    client_text = '''
    Work for the ticket:
    "{title}"
    has been completed.

    You will be charged ${price}.

    Thank you for your business.

    The Rebase Team
    '''.format(
        title=ticket.title,
        price=work.debit.price
    )
    client_email = Email(
        'do_not_reply@rebaseapp.com',
        managers_emails,
        'Rebase: completed ticket "{}"'.format(ticket.title),
        client_text,
        client_text,
    )
    send([ contractor_email, client_email ])
