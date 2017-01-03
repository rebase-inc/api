from functools import lru_cache
from logging import getLogger
from urllib.parse import urlparse

from flask_oauthlib.client import OAuth

from ..common import config
from ..models import GithubOAuthApp


logger = getLogger()

OAUTH_SETTINGS = {
    'request_token_params': {'scope': 'user, repo'},
    'base_url': 'https://api.github.com/',
    'request_token_url': None,
    'access_token_method': 'POST',
    'access_token_url': 'https://github.com/login/oauth/access_token',
    'authorize_url': 'https://github.com/login/oauth/authorize'
}

def apps(app):
    oauth = OAuth(app)
    skillgraph = GithubOAuthApp.query.filter_by(name='skillgraph').first()
    oauth_app = oauth.remote_app(
            skillgraph.name,
            consumer_key = skillgraph.client_id,
            consumer_secret = config.GITHUB_APP_CLIENT_SECRET,
            **OAUTH_SETTINGS
    )
    attribute = 'github_app'
    setattr(oauth_app, attribute, skillgraph)
    return { urlparse(skillgraph.url).hostname: oauth_app }


def oauth_app_from_github_account(apps, account):
    return apps[urlparse(account.app.url).hostname]


