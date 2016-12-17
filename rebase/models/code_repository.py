from rebase.common.database import DB, PermissionMixin

class CodeRepository(DB.Model, PermissionMixin):
    __pluralname__ = 'code_repositories'

    id =   DB.Column(DB.Integer, primary_key=True)
    type = DB.Column(DB.String)
    url =  DB.Column(DB.String, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'code_repository',
        'polymorphic_on': type
    }

    def __init__(self, url):
        self.url = url

    @classmethod
    def setup_queries(cls, models):
        cls.filter_based_on_current_role = False
        cls.as_owner_path = [
            models.Project,
            models.Organization,
            models.Owner,
        ]
        cls.as_contractor_path = [
            models.Project,
            models.CodeClearance,
            models.Contractor,
        ]
        cls.as_manager_path = [
            models.Project,
            models.Manager
        ]

    def allowed_to_be_created_by(self, user):
        return self.project.allowed_to_be_created_by(user)

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.found(self, user)

    def __repr__(self):
        return '<CodeRepository[id:{}]>'.format(self.id)

