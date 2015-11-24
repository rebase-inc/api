from rebase.common.database import DB, PermissionMixin

class Role(DB.Model, PermissionMixin):
    __pluralname__ = 'roles'

    id =      DB.Column(DB.Integer, primary_key=True)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    type =    DB.Column(DB.String)

    __mapper_args__ = {
        'polymorphic_identity': 'role',
        'polymorphic_on': type
    }

    def __init__(self):
        raise NotImplemented()

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
        return '<User[id:{}] name={} email={}>'.format(self.id, self.name, self.email)
