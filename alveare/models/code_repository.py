from alveare.common.database import DB, PermissionMixin, query_by_user_or_id

class CodeRepository(DB.Model, PermissionMixin):
    __pluralname__ = 'code_repositories'

    id =   DB.Column(DB.Integer, DB.ForeignKey('project.id', ondelete='CASCADE'), primary_key=True)
    url =  DB.Column(DB.String, nullable=True)

    def __init__(self, project, url=None):
        self.project = project
        self.url = url

    @classmethod
    def query_by_user(cls, user):
        return query_by_user_or_id(cls, cls.get_all, user)

    @classmethod
    def get_all(cls, user, id=None):
        return cls.as_manager(user, id)\
            .union(cls.as_cleared_contractor(user, id))

    @classmethod
    def as_manager(cls, user, id=None):
        import alveare.models.project
        query = cls.query
        if id:
            query = query.filter(cls.id==id)
        return query\
            .join(alveare.models.project.Project)\
            .join(alveare.models.organization.Organization)\
            .join(alveare.models.manager.Manager)\
            .filter(alveare.models.manager.Manager.user==user)

    @classmethod
    def as_cleared_contractor(cls, user, id=None):
        import alveare.models.project
        query = cls.query
        if id:
            query = query.filter(cls.id==id)
        return query\
            .join(alveare.models.project.Project)\
            .join(alveare.models.code_clearance.CodeClearance)\
            .join(alveare.models.contractor.Contractor)\
            .filter(alveare.models.contractor.Contractor.user==user)

    def allowed_to_be_created_by(self, user):
        if user.admin:
            return True
        return self.as_manager(user, self.id).all()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        if user.admin:
            return True
        return self.get_all(user, self.id).all()

    def __repr__(self):
        return '<CodeRepository[id:{}]>'.format(self.id)

