
from rebase.common.database import DB, PermissionMixin


class SkillRankings(DB.Model, PermissionMixin):
    __pluralname__ = 'skill_sets'

    id =            DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), primary_key=True)
    rankings =      DB.Column(DB.PickleType, nullable=True)

    def __init__(self):
        self.rankings = None

    @classmethod
    def setup_queries(cls, models):
        cls.as_owner_path = []
        cls.as_contractor_path = []
        cls.as_manager_path = []

    def allowed_to_be_created_by(self, user):
        return user.admin

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return True

    def __repr__(self):
        return '<SkillRankings[{}]>'.format(self.id)


