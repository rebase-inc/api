
from rebase.common.database import DB, PermissionMixin

class GithubOrgAccount(DB.Model, PermissionMixin):
    __pluralname__ = 'github_org_accounts'

    org_id =        DB.Column(DB.Integer, DB.ForeignKey('github_organization.id',   ondelete='CASCADE'), primary_key=True)
    account_id =    DB.Column(DB.Integer, DB.ForeignKey('github_account.id',        ondelete='CASCADE'), primary_key=True)

    def __init__(self, github_organization, github_account):
        self.org = github_organization
        self.account = github_account

    def allowed_to_be_created_by(self, user):
        return user.admin

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.org.allowed_to_be_viewed_by(user)

    def __repr__(self):
        return '<GithubOrgAccount[{}, {}]>'.format(self.org_id, self.account_id)

    @classmethod
    def setup_queries(cls, models):
        cls.as_owner_path = [
            models.GithubOrganization,
            models.Owner,
        ]
        cls.as_contractor_path = [
            models.GithubOrganization,
            models.CodeClearance,
            models.Contractor,
        ]

        cls.as_manager_path = [
            models.GithubOrganization,
            models.Manager
        ]
