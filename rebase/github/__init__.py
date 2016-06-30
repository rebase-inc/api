from copy import copy
from functools import lru_cache
from logging import getLogger
from re import compile as re_compile
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


relations = frozenset(['first', 'prev', 'next', 'last'])


re_link = re_compile(r'^\s*<(?P<link>https://api\.github\.com/.*)>; rel="(?P<rel>first|prev|next|last)"$')


class InvalidLinksHeader(Exception):
    def __init__(self, links_header):
        self.message = 'Invalid Links header: '+links_header


def pagination(link_header):
    '''
    Return a dict with keys in ('first', 'prev', 'next', 'last')
    For each relationship to the current page, the value is the HTTP link to the corresponding page.
    '''
    links = link_header.split(',')
    pages = dict()
    for link in links:
        match = re_link.fullmatch(link) 
        if not match:
            raise InvalidLinksHeader(link_header)
        pages[match.group('rel')] = match.group('link')
    assert set(pages.keys()).issubset(relations)
    return pages


class GithubApi(object):
    '''Base class to read data from Github's API.
    We need this to write code that works with either Flask-OAuthlib or Requests.
    (Our crawler does not depend on Flask)
    '''

    def __init__(self):
        self.data = None
        self.status = None
        self.headers = None

    def get_raw(url_or_path, *args, **kwargs):
        '''
        Return a tuple (response, data) where response is the raw response
        from the underlying implementation and data is the JSON decoded body
        of the response
        '''
        raise NotImplemented('GithubApi.get_raw is abstract')

    def get(self, url_or_path, *args, **kwargs):
        ''' return a JSON object, given a Github URL or a Github path '''
        self.get_raw(url_or_path, *args, **kwargs)
        if self.status >= 400 and self.status <= 599:
            pdebug(self.data, 'data')
            raise GithubException(self.status, self.data['message'])
        return self.data

    def rate_limit(self):
        return self.get('/rate_limit')

    def for_each_page(self, url_or_path, handle_one_page, *args, **kwargs):
        _url = url_or_path
        while True:
            self.get_raw(_url, *args, **kwargs)
            handle_one_page(self.data)
            if 'Link' not in self.headers:
                break
            pages = pagination(self.headers['Link'])
            if 'next' in pages:
                _url = pages['next']
            else:
                break


class GithubException(Exception):

    def __init__(self, status, message):
        self.status = status
        self.message = message

    
class GithubApiRequests(GithubApi):

    def __init__(self, username, token):
        self.root_url = 'https://api.github.com'
        self.session = Session()
        self.session.auth = (username, token)
        super().__init__()

    def get_raw(self, path, *args, **kwargs):
        full_path = path if path.startswith('http') else self.root_url+path
        response = self.session.get(full_path, *args, **kwargs)
        self.data = response.json()
        self.status = response.status_code
        self.headers = response.headers

    def close(self):
        self.session.close()


class GithubApiFlaskOAuthlib(GithubApi):

    def __init__(self, flask_oauth_api):
        self.api = flask_oauth_api
        super().__init__()

    def get_raw(self, url_or_path, *args, **kwargs):
        response = self.api.get(url_or_path, *args, **kwargs)
        self.data = response.data
        self.status = response.status
        self.headers = response._resp.headers


