
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
        return cls.get_all(user)

    def filter_by_id(self, query):
        return query.filter(SkillSet.id==self.id)

    @classmethod
    def get_all(cls, user, skill_set=None):
        return query_by_user_or_id(
            cls,
            lambda user: cls.as_manager(user).union(cls.as_contractor(user)),
            cls.filter_by_id,
            user, skill_set
        )

    @classmethod
    def as_manager(cls, user):
        import alveare.models
        return query_from_class_to_user(SkillSet, [
            alveare.models.contractor.Contractor,
            alveare.models.code_clearance.CodeClearance,
            alveare.models.project.Project,
            alveare.models.organization.Organization,
            alveare.models.manager.Manager,
        ], user)

    @classmethod
    def as_contractor(cls, user):
        import alveare.models
        return query_from_class_to_user(SkillSet, [
            alveare.models.contractor.Contractor,
        ], user)

    def allowed_to_be_created_by(self, user):
        return user.admin

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.get_all(user, self).limit(1).all()

    def __repr__(self):
        return '<SkillSet[{}]>'.format(self.id)
