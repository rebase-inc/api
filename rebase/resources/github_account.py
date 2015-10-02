from flask.ext.restful import Resource
from flask.ext.login import login_required, current_user, current_app
from flask import jsonify, make_response, request

from rebase.github.scanners import make_session, extract_repos_info
from rebase.models import GithubAccount
from rebase.views import github_account as views
from rebase.common.database import DB
from rebase.common.rest import get_collection, add_to_collection

def get_github_account_info(account):
    session = make_session(account, current_app, current_user, DB)
    return extract_repos_info(session)

class GithubAccountCollection(Resource):
    model = GithubAccount
    serializer = views.serializer
    deserializer = views.deserializer
    url = '/{}'.format(model.__pluralname__)

    @login_required
    def get(self):
        def fetch_account_info(accounts):
            for account in accounts:
                get_github_account_info(account)
            return accounts
        return get_collection(self.model, self.serializer, pre_serialization=fetch_account_info)

    @login_required
    def post(self):
        return add_to_collection(self.model, self.deserializer, self.serializer)
