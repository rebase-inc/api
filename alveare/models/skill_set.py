
from alveare.common.database import DB, PermissionMixin, query_by_user_or_id
from alveare.common.query import query_from_class_to_user

class SkillSet(DB.Model, PermissionMixin):
    __pluralname__ = 'skill_sets'

    id =  DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), primary_key=True)

    ticket_matches = DB.relationship('TicketMatch', backref='skill_set', cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, contractor):
        self.contractor = contractor

    @classmethod
    def query_by_user(cls, user):
        return query_by_user_or_id(cls, cls.get_all, user)

    @classmethod
    def get_all(cls, user, id=None):
        return cls.as_manager(user, id).union(cls.as_contractor(user, id))

    @classmethod
    def as_manager(cls, user, id=None):
        import alveare.models
        return query_from_class_to_user(SkillSet, [
            alveare.models.contractor.Contractor,
            alveare.models.code_clearance.CodeClearance,
            alveare.models.project.Project,
            alveare.models.organization.Organization,
            alveare.models.manager.Manager,
        ], user, id)

    @classmethod
    def as_contractor(cls, user, id=None):
        import alveare.models
        return query_from_class_to_user(SkillSet, [
            alveare.models.contractor.Contractor,
        ], user, id)

    def allowed_to_be_created_by(self, user):
        if user.admin:
            return True
        return self.as_contractor(user, self.id).limit(1).all()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        if user.admin:
            return True
        return self.get_all(user, self.id).limit(1).all()

    def __repr__(self):
        return '<SkillSet[{}]>'.format(self.id)
