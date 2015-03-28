
from alveare.common.database import DB, PermissionMixin

class TermSheet(DB.Model, PermissionMixin):
    __pluralname__ = 'term_sheets'

    id = DB.Column(DB.Integer, primary_key=True)
    legalese = DB.Column(DB.String, nullable=False)

    def __init__(self, legalese):
        self.legalese = legalese

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
        return '<TermSheet[id:{}]>'.format(self.id)

