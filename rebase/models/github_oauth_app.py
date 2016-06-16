
from sqlalchemy.orm import reconstructor

from rebase.common.database import DB, PermissionMixin


class GithubOAuthApp(DB.Model, PermissionMixin):
    __pluralname__ = 'github_oauth_apps'

    client_id = DB.Column(DB.String, unique=True, primary_key=True)
    name =      DB.Column(DB.String, nullable=False, unique=True)
    url =       DB.Column(DB.String, nullable=False)
    accounts =  DB.relationship('GithubAccount', backref='app', cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, client_id, name, url):
        self.client_id = client_id
        # Client Secret will be retrieved from the host environment and made accessible via app.config
        self.name = name
        self.url = url

    def query_by_user(user):
        if user.is_admin():
            return GithubAccount.query
        return GithubAccount.query.filter(GithubAccount.user==user)

    def allowed_to_be_created_by(self, user):
        return user.is_admin()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return True

    def __repr__(self):
        return '<GithubOAuthApp(name={}, ClientID={}, URL={})>'.format(self.name, self.client_id, self.url)

    @classmethod
    def setup_queries(cls, models):
        cls.as_contractor_path = cls.as_manager_path = []


