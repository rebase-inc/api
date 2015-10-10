
from rebase.common.database import DB, PermissionMixin, query_by_user_or_id
from rebase.common.query import query_from_class_to_user

class SkillSet(DB.Model, PermissionMixin):
    __pluralname__ = 'skill_sets'

    id =  DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), primary_key=True)
    skills =  DB.Column(DB.PickleType, nullable=True)

    ticket_matches = DB.relationship('TicketMatch', backref='skill_set', cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, contractor, skills=None):
        self.contractor = contractor
        self.skills = skills or {}

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
        import rebase.models
        return query_from_class_to_user(SkillSet, [
            rebase.models.contractor.Contractor,
            rebase.models.code_clearance.CodeClearance,
            rebase.models.project.Project,
            rebase.models.organization.Organization,
            rebase.models.manager.Manager,
        ], user)

    @classmethod
    def as_contractor(cls, user):
        import rebase.models
        return query_from_class_to_user(SkillSet, [
            rebase.models.contractor.Contractor,
        ], user)

    def allowed_to_be_created_by(self, user):
        return user.admin

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return True
        return self.get_all(user, self).limit(1).all()

    def __repr__(self):
        return '<SkillSet[{}]>'.format(self.id)
