from sqlalchemy.orm import validates

from rebase.common.database import DB, PermissionMixin

class Photo(DB.Model, PermissionMixin):
    __pluralname__ = 'photos'

    id =       DB.Column(DB.Integer, primary_key=True)
    user_id =  DB.Column(DB.Integer, DB.ForeignKey('user.id'), nullable=False)
    filename = DB.Column(DB.String, nullable=False)

    def __init__(self, filename, user):
        self.filename = filename
        self.user = user

    @property
    def url(self):
        return '/uploads/{}'.format(self.filename)

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
        return '<Photo[{}] for {} at {}>'.format(self.id, self.user, self.filename)
