from alveare.common.database import DB, PermissionMixin, query_by_user_or_id
from alveare.common.query import query_from_class_to_user

class CodeRepository(DB.Model, PermissionMixin):
    __pluralname__ = 'code_repositories'

    id =   DB.Column(DB.Integer, DB.ForeignKey('project.id', ondelete='CASCADE'), primary_key=True)
    url =  DB.Column(DB.String, nullable=True)

    def __init__(self, project, url=None):
        self.project = project
        self.url = url

    @classmethod
    def query_by_user(cls, user):
        return cls.get_all(user)

    def filter_by_id(self, query):
        return query.filter(CodeRepository.id==self.id)

    @classmethod
    def get_all(cls, user, repo=None):
        return query_by_user_or_id(
            cls,
            lambda user: cls.as_manager(user).union(cls.as_contractor(user)),
            cls.filter_by_id,
            user, repo
        )

    @classmethod
    def as_manager(cls, user):
        import alveare.models.project
        return query_from_class_to_user(CodeRepository, [
            alveare.models.project.Project,
            alveare.models.organization.Organization,
            alveare.models.manager.Manager,
        ], user)

    @classmethod
    def as_contractor(cls, user, id=None):
        import alveare.models.project
        return query_from_class_to_user(CodeRepository, [
            alveare.models.project.Project,
            alveare.models.code_clearance.CodeClearance,
            alveare.models.contractor.Contractor,
        ], user)

    def allowed_to_be_created_by(self, user):
        return self.project.allowed_to_be_modified_by(user)

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.get_all(user, self).all()

    def __repr__(self):
        return '<CodeRepository[id:{}]>'.format(self.id)

