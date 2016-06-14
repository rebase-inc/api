
from rebase.common.database import DB, PermissionMixin
from rebase.models.github_account import GithubAccount


class GithubOrgAccount(DB.Model, PermissionMixin):
    __pluralname__ = 'github_org_accounts'

    org_id =            DB.Column(DB.Integer, DB.ForeignKey('github_organization.id', ondelete='CASCADE'), primary_key=True)
    app_id =            DB.Column(DB.String,  primary_key=True)
    github_user_id =    DB.Column(DB.Integer, primary_key=True)
    user_id =           DB.Column(DB.Integer, primary_key=True)

    __table_args__ = (
        DB.ForeignKeyConstraint(
            [app_id, github_user_id, user_id],
            [GithubAccount.app_id, GithubAccount.github_user_id, GithubAccount.user_id],
            ondelete='CASCADE'
        ), {})

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
        return '<GithubOrgAccount({})>'.format(
            self.org_id,
            self.app_id,
            self.github_user_id,
            self.user_id,
        )

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
