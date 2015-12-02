from datetime import datetime

from rebase.common.database import DB, PermissionMixin, query_by_user_or_id
from rebase.common.query import query_from_class_to_user

class Comment(DB.Model, PermissionMixin):
    __pluralname__ = 'comments'

    id =        DB.Column(DB.Integer, primary_key=True)
    content =   DB.Column(DB.String,  nullable=False)
    created =   DB.Column(DB.DateTime, nullable=False)

    work_id =       DB.Column(DB.Integer, DB.ForeignKey('work.id',      ondelete='CASCADE'),    nullable=True)
    review_id =     DB.Column(DB.Integer, DB.ForeignKey('review.id',    ondelete='CASCADE'),    nullable=True)
    mediation_id =  DB.Column(DB.Integer, DB.ForeignKey('mediation.id', ondelete='CASCADE'),    nullable=True)
    ticket_id =     DB.Column(DB.Integer, DB.ForeignKey('ticket.id',    ondelete='CASCADE'),    nullable=True)
    feedback_id =   DB.Column(DB.Integer, DB.ForeignKey('feedback.id',  ondelete='CASCADE'),    nullable=True)

    user_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'), nullable=False)
    user = DB.relationship('User', uselist=False)

    def __init__(self, user, content, created=None, work=None, review=None, mediation=None, ticket=None, feedback=None):
        self.user = user
        self.content = content
        self.created = created or datetime.now()
        self.work = work
        self.review = review
        self.mediation = mediation
        self.ticket = ticket
        self.feedback = feedback

    @classmethod
    def query_by_user(cls, user):
        return cls.get_all(user)

    def filter_by_id(self, query):
        return query.filter(Comment.id==self.id)

    @classmethod
    def get_all(cls, user, comment=None):
        return query_by_user_or_id(
            cls,
            lambda user: cls.as_manager(user).union(cls.as_contractor(user)),
            cls.filter_by_id,
            user, comment
        )

    @classmethod
    def as_manager(cls, user):
        return cls.get_manager_ticket_comment(user)\
            .union(cls.get_manager_mediation_comment(user))\
            .union(cls.get_manager_work_comment(user))\
            .union(cls.get_manager_review_comment(user))\
            .union(cls.get_manager_feedback_comment(user))

    def get_manager_ticket_comment(user):
        import rebase.models
        return query_from_class_to_user(Comment, [
            rebase.models.ticket.Ticket,
            rebase.models.project.Project,
            rebase.models.organization.Organization,
            rebase.models.manager.Manager,
        ], user)

    def get_manager_feedback_comment(user):
        import rebase.models
        return query_from_class_to_user(Comment, [
            rebase.models.feedback.Feedback,
            rebase.models.auction.Auction,
            rebase.models.ticket_set.TicketSet,
            rebase.models.bid_limit.BidLimit,
            rebase.models.ticket_snapshot.TicketSnapshot,
            rebase.models.ticket.Ticket,
            rebase.models.project.Project,
            rebase.models.organization.Organization,
            rebase.models.manager.Manager,
        ], user)

    def get_manager_mediation_comment(user):
        import rebase.models
        return query_from_class_to_user(Comment, [
            rebase.models.mediation.Mediation,
            rebase.models.work.Work,
            rebase.models.work_offer.WorkOffer,
            rebase.models.ticket_snapshot.TicketSnapshot,
            rebase.models.ticket.Ticket,
            rebase.models.project.Project,
            rebase.models.organization.Organization,
            rebase.models.manager.Manager,
        ], user)

    def get_manager_review_comment(user):
        import rebase.models
        return query_from_class_to_user(Comment, [
            rebase.models.review.Review,
            rebase.models.work.Work,
            rebase.models.work_offer.WorkOffer,
            rebase.models.ticket_snapshot.TicketSnapshot,
            rebase.models.ticket.Ticket,
            rebase.models.project.Project,
            rebase.models.organization.Organization,
            rebase.models.manager.Manager,
        ], user)

    def get_manager_work_comment(user):
        import rebase.models
        return query_from_class_to_user(Comment, [
            rebase.models.work.Work,
            rebase.models.work_offer.WorkOffer,
            rebase.models.ticket_snapshot.TicketSnapshot,
            rebase.models.ticket.Ticket,
            rebase.models.project.Project,
            rebase.models.organization.Organization,
            rebase.models.manager.Manager,
        ], user)

    @classmethod
    def as_contractor(cls, user):
        return cls.get_contractor_ticket_comment(user)\
            .union(cls.get_contractor_mediation_comment(user))\
            .union(cls.get_contractor_work_comment(user))\
            .union(cls.get_contractor_review_comment(user))\
            .union(cls.get_contractor_feedback_comment(user))

    def get_contractor_ticket_comment(user):
        import rebase.models
        return query_from_class_to_user(Comment, [
            rebase.models.ticket.Ticket,
            rebase.models.project.Project,
            rebase.models.code_clearance.CodeClearance,
            rebase.models.contractor.Contractor,
        ], user)

    def get_contractor_feedback_comment(user):
        import rebase.models
        return query_from_class_to_user(Comment, [
            rebase.models.feedback.Feedback,
            rebase.models.contractor.Contractor,
        ], user)

    def get_contractor_mediation_comment(user):
        import rebase.models
        return query_from_class_to_user(Comment, [
            rebase.models.mediation.Mediation,
            rebase.models.work.Work,
            rebase.models.work_offer.WorkOffer,
            rebase.models.contractor.Contractor,
        ], user)

    def get_contractor_work_comment(user):
        import rebase.models
        return query_from_class_to_user(Comment, [
            rebase.models.work.Work,
            rebase.models.work_offer.WorkOffer,
            rebase.models.contractor.Contractor,
        ], user)

    def get_contractor_review_comment(user):
        import rebase.models
        return query_from_class_to_user(Comment, [
            rebase.models.review.Review,
            rebase.models.work.Work,
            rebase.models.work_offer.WorkOffer,
            rebase.models.contractor.Contractor,
        ], user)

    def allowed_to_be_created_by(self, user):
        if user.admin:
            return True
        if self.work:
            return self.work.allowed_to_be_viewed_by(user)
        if self.review:
            return self.review.allowed_to_be_viewed_by(user)
        if self.mediation:
            return self.mediation.allowed_to_be_viewed_by(user)
        if self.ticket:
            return self.ticket.allowed_to_be_viewed_by(user)
        if self.feedback:
            return self.feedback.allowed_to_be_modified_by(user)
        raise ValueError('Invalid Comment object')

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        if user.admin:
            return True
        if self.work:
            return self.work.allowed_to_be_viewed_by(user)
        if self.review:
            return self.review.allowed_to_be_viewed_by(user)
        if self.mediation:
            return self.mediation.allowed_to_be_viewed_by(user)
        if self.ticket:
            return self.ticket.allowed_to_be_viewed_by(user)
        if self.feedback:
            return self.feedback.allowed_to_be_viewed_by(user)
        raise ValueError('Invalid Comment object')

    def __repr__(self):
        abbreviated_content = self.content[0:15]
        if self.content != abbreviated_content:
            abbreviated_content += '...'
        return '<Comment[{}] "{}">'.format(self.id, abbreviated_content)

