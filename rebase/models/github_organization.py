
from rebase.common.database import DB, PermissionMixin
from rebase.models import Manager, Organization

class GithubOrganization(Organization):
    __pluralname__ = 'github_repositories'

    id =            DB.Column(DB.Integer, DB.ForeignKey('organization.id', ondelete='CASCADE'), primary_key=True)
    login =         DB.Column(DB.String, nullable=False)
    org_id =        DB.Column(DB.Integer, nullable=False, unique=True)
    url =           DB.Column(DB.String, nullable=False)
    description =   DB.Column(DB.String, nullable=True)

    accounts = DB.relationship('GithubOrgAccount', backref='org', cascade="all, delete-orphan", passive_deletes=True)

    __mapper_args__ = { 'polymorphic_identity': 'github_organization' }

    def __init__(self, login, user, org_id, url, description):
        self.login = login
        self.org_id = org_id
        self.url = url
        self.description = description
        super().__init__(self.login, user)

    def allowed_to_be_created_by(self, user):
        return user.is_admin()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return True

    def __repr__(self):
        return '<GithubOrganization[{}]>'.format(self.id)

    @classmethod
    def setup_queries(cls, models):
        # TODO fix contractor query permissions
        cls.as_contractor_path = [
            models.Organization,
            models.Manager
        ]
        cls.as_manager_path = [
            models.Organization,
            models.Manager
        ]
