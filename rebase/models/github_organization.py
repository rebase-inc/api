
from rebase.common.database import DB, PermissionMixin

class GithubOrganization(DB.Model, PermissionMixin):
    __pluralname__ = 'github_repositories'

    id =            DB.Column(DB.Integer, primary_key=True)
    account_id =    DB.Column(DB.Integer, DB.ForeignKey('github_account.id', ondelete='CASCADE'))
    login =         DB.Column(DB.String, nullable=False)
    org_id =        DB.Column(DB.Integer, nullable=False, unique=True)
    url =           DB.Column(DB.String, nullable=False)
    description =   DB.Column(DB.String, nullable=True)

    repos =         DB.relationship('GithubRepository', lazy='dynamic', backref='org', cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, account, login, org_id, url, description):
        import pdb; pdb.set_trace()
        self.account = account
        self.login = login
        self.org_id = org_id
        self.url = url
        self.description = description

    def allowed_to_be_created_by(self, user):
        return user.is_admin()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return user.is_admin() or self.account.user == user

    def __repr__(self):
        return '<GithubOrganization[{}]>'.format(self.id)

    @classmethod
    def setup_queries(cls, models):
        cls.as_manager_path = cls.as_contractor_path = [
            models.GithubAccount
        ]
