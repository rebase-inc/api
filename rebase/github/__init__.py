from copy import copy
from functools import lru_cache
from logging import getLogger
from re import compile, MULTILINE
from urllib.parse import urlparse

from flask_oauthlib.client import OAuth
from requests import get, Session

from rebase.common.debug import pdebug
from rebase.models import GithubOAuthApp


logger = getLogger()


@lru_cache()
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


class GithubApi(object):
    '''Base class to read data from Github's API.
    We need this to write code that works with either Flask-OAuthlib or Requests.
    (Our crawler does not depend on Flask)
    '''

    def get(url_or_path, *args, **kwargs):
        ''' return a JSON object, given a Github URL or a Github path '''
        raise NotImplemented('GithubApi.get is abstract')


class GithubException(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message

    
class GithubApiRequests(GithubApi):
    def __init__(self, username, token):
        self.root_url = 'https://api.github.com'
        self.session = Session()
        self.session.auth = (username, token)

    def get(self, path, *args, **kwargs):
        full_path = path if path.startswith('http') else self.root_url+path
        #logger.debug('GithubApiRequests.get: %s', full_path)
        response = self.session.get(full_path, *args, **kwargs)
        pdebug(response.text, 'response.text')
        pdebug(response.headers, 'GithubApiRequests.get, response.headers: %s')
        response_data = response.json()
        if response.status_code >= 400 and response.status_code <= 599:
            pdebug(response_data, 'response_data')
            raise GithubException(response.status_code, response_data['message'])
        #pdebug(response_data, 'GithubApiRequests.get, response_data: %s')
        return response_data

    def close(self):
        self.session.close()


class GithubApiFlaskOAuthlib(GithubApi):
    def __init__(self, flask_oauth_api):
        self.api = flask_oauth_api

    def get(self, url_or_path, *args, **kwargs):
        return self.api.get(url_or_path, *args, **kwargs).data


