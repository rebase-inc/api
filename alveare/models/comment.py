from alveare.common.database import DB, PermissionMixin, query_by_user_or_id
from alveare.common.query import query_from_class_to_user

class Comment(DB.Model, PermissionMixin):
    __pluralname__ = 'comments'

    id =        DB.Column(DB.Integer, primary_key=True)
    content =   DB.Column(DB.String,  nullable=False)

    review_id =     DB.Column(DB.Integer, DB.ForeignKey('review.id',    ondelete='CASCADE'),    nullable=True)
    mediation_id =  DB.Column(DB.Integer, DB.ForeignKey('mediation.id', ondelete='CASCADE'),    nullable=True)
    ticket_id =     DB.Column(DB.Integer, DB.ForeignKey('ticket.id',    ondelete='CASCADE'),    nullable=True)
    feedback_id =   DB.Column(DB.Integer, DB.ForeignKey('feedback.id',  ondelete='CASCADE'),    nullable=True)

    def __init__(self, content=None, review=None, mediation=None, ticket=None, feedback=None):
        self.content = content
        self.review = review
        self.mediation = mediation
        self.ticket = ticket
        self.feedback = feedback

    @classmethod
    def query_by_user(cls, user):
        return query_by_user_or_id(cls, cls.get_all, user)

    @classmethod
    def get_all(cls, user, id=None):
        return cls.as_manager(user, id)\
            .union(cls.as_contractor(user, id))

    @classmethod
    def as_manager(cls, user, id=None):
        return cls.get_manager_ticket_comment(user, id)\
            .union(cls.get_manager_mediation_comment(user, id))\
            .union(cls.get_manager_review_comment(user, id))\
            .union(cls.get_manager_feedback_comment(user, id))

    def get_manager_ticket_comment(user, id=None):
        import alveare.models
        return query_from_class_to_user(Comment, [
            alveare.models.ticket.Ticket,
            alveare.models.project.Project,
            alveare.models.organization.Organization,
            alveare.models.manager.Manager,
        ], user, id)

    def get_manager_feedback_comment(user, id=None):
        import alveare.models
        return query_from_class_to_user(Comment, [
            alveare.models.feedback.Feedback,
            alveare.models.auction.Auction,
            alveare.models.ticket_set.TicketSet,
            alveare.models.bid_limit.BidLimit,
            alveare.models.ticket_snapshot.TicketSnapshot,
            alveare.models.ticket.Ticket,
            alveare.models.project.Project,
            alveare.models.organization.Organization,
            alveare.models.manager.Manager,
        ], user, id)

    def get_manager_mediation_comment(user, id=None):
        import alveare.models
        return query_from_class_to_user(Comment, [
            alveare.models.mediation.Mediation,
            alveare.models.work.Work,
            alveare.models.work_offer.WorkOffer,
            alveare.models.ticket_snapshot.TicketSnapshot,
            alveare.models.ticket.Ticket,
            alveare.models.project.Project,
            alveare.models.organization.Organization,
            alveare.models.manager.Manager,
        ], user, id)

    def get_manager_review_comment(user, id=None):
        import alveare.models
        return query_from_class_to_user(Comment, [
            alveare.models.review.Review,
            alveare.models.work.Work,
            alveare.models.work_offer.WorkOffer,
            alveare.models.ticket_snapshot.TicketSnapshot,
            alveare.models.ticket.Ticket,
            alveare.models.project.Project,
            alveare.models.organization.Organization,
            alveare.models.manager.Manager,
        ], user, id)

    @classmethod
    def as_contractor(cls, user, id=None):
        return cls.get_contractor_ticket_comment(user, id)\
            .union(cls.get_contractor_mediation_comment(user, id))\
            .union(cls.get_contractor_review_comment(user, id))\
            .union(cls.get_contractor_feedback_comment(user, id))

    def get_contractor_ticket_comment(user, id=None):
        import alveare.models
        return query_from_class_to_user(Comment, [
            alveare.models.ticket.Ticket,
            alveare.models.project.Project,
            alveare.models.code_clearance.CodeClearance,
            alveare.models.contractor.Contractor,
        ], user, id)

    def get_contractor_feedback_comment(user, id=None):
        import alveare.models
        return query_from_class_to_user(Comment, [
            alveare.models.feedback.Feedback,
            alveare.models.contractor.Contractor,
        ], user, id)

    def get_contractor_mediation_comment(user, id=None):
        import alveare.models
        return query_from_class_to_user(Comment, [
            alveare.models.mediation.Mediation,
            alveare.models.work.Work,
            alveare.models.work_offer.WorkOffer,
            alveare.models.contractor.Contractor,
        ], user, id)

    def get_contractor_review_comment(user, id=None):
        import alveare.models
        return query_from_class_to_user(Comment, [
            alveare.models.review.Review,
            alveare.models.work.Work,
            alveare.models.work_offer.WorkOffer,
            alveare.models.contractor.Contractor,
        ], user, id)

    def allowed_to_be_created_by(self, user):
        if user.admin:
            return True
        return self.get_all(user, self.id).all()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        if user.admin:
            return True
        return self.get_all(user, self.id).all()

    def __repr__(self):
        abbreviated_content = self.content[0:15]
        if self.content != abbreviated_content:
            abbreviated_content += '...'
        return '<Comment[{}] "{}">'.format(self.id, abbreviated_content)

