
from rebase.common.database import DB, PermissionMixin

class GithubContributedRepo(DB.Model, PermissionMixin):
    __pluralname__ = 'github_org_accounts'

    id =          DB.Column(DB.Integer, primary_key=True)
    account_id =  DB.Column(DB.Integer, DB.ForeignKey('github_account.id', ondelete='CASCADE'))
    github_id =   DB.Column(DB.Integer)
    name =        DB.Column(DB.String)
    description = DB.Column(DB.String)
    owner =       DB.Column(DB.String)

    def __init__(self, remote_work_history, account, github_id, name, description, owner):
        self.remote_work_history = remote_work_history
        self.account = account
        self.github_id = github_id
        self.name = name
        self.description = description
        self.owner = owner

    def allowed_to_be_created_by(self, user):
        return user.admin

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.remote_work_history.contractor.allowed_to_be_viewed_by(user)

    def __repr__(self):
        return '<GithubContributedRepo[{}]>'.format(self.id)

    @classmethod
    def setup_queries(cls, models):
        cls.as_owner_path = [
            models.RemoteWorkHistory,
            models.Contractor,
            models.CodeClearance,
            models.Project,
            models.Organization,
            models.Owner,
        ]
        cls.as_contractor_path = [
            models.RemoteWorkHistory,
            models.Contractor,
        ]

        cls.as_manager_path = [
            models.RemoteWorkHistory,
            models.Contractor,
            models.CodeClearance,
            models.Project,
            models.Manager
        ]
