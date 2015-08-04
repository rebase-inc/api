
from rebase.common.database import DB, PermissionMixin

class TalentPool(DB.Model, PermissionMixin):
    __pluralname__ = 'talent_pools'

    id = DB.Column(DB.Integer, primary_key=True)

    @classmethod
    def query_by_user(cls, user):
        return cls.query

    def allowed_to_be_created_by(self, user):
        return True

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        return self.allowed_to_be_created_by(user)

    def __repr__(self):
        return '<TalentPool[id:{}]>'.format(self.id)

