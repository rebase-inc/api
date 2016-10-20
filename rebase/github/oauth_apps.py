from functools import lru_cache
from logging import getLogger
from urllib.parse import urlparse

from flask_oauthlib.client import OAuth

from rebase.models import GithubOAuthApp


logger = getLogger()


def apps(app):
    oauth = OAuth(app)
    common_settings = {
            'request_token_params': {'scope': 'user, repo'},
            'base_url': 'https://api.github.com/',
            'request_token_url': None,
            'access_token_method': 'POST',
            'access_token_url': 'https://github.com/login/oauth/access_token',
            'authorize_url': 'https://github.com/login/oauth/authorize'
    }
    alpha = GithubOAuthApp.query.filter_by(name='alpha').first()
    code2resume = GithubOAuthApp.query.filter_by(name='code2resume').first()
    alpha_app = oauth.remote_app(
            alpha.name,
            consumer_key=alpha.client_id,
            consumer_secret=app.config['GITHUB_APP_SECRET'],
            **common_settings
    )
    attribute =  'github_app'
    setattr(alpha_app, attribute, alpha)
    code2resume_app = oauth.remote_app(
            code2resume.name,
            consumer_key=code2resume.client_id,
            consumer_secret=app.config['GITHUB_CODE2RESUME_SECRET'],
            **common_settings
    )
    setattr(code2resume_app, attribute, code2resume)
    return {
        urlparse(alpha.url).hostname:       alpha_app,
        urlparse(code2resume.url).hostname: code2resume_app
    }


def oauth_app_from_github_account(apps, account):
    return apps[urlparse(account.app.url).hostname]


