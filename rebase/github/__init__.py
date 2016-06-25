from copy import copy
from functools import lru_cache
from logging import getLogger
from re import compile, MULTILINE
from urllib.parse import urlparse

from diff_match_patch import diff_match_patch as dmp
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


re_diff_headers = compile("^(@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@)", flags=MULTILINE)
    

def reverse(patches):
    ''' return a list of reversed patches.
    Reversed patches can be applied to the new file to retrieve the old file
    '''
    reverse_patches = []
    for patch in patches:
        new_patch = copy(patch)
        reverse_patches.append(new_patch)
        new_diffs = []
        for diff in new_patch.diffs:
            # works because the library implementation uses 1 for insert and -1 for delete.
            # a more future-proof code would use if diff[0] == DIFF_INSERT ....
            new_diffs.append( (-1*diff[0], diff[1]) )
        new_patch.diffs = new_diffs
    return reverse_patches


def old_version(new, patches_as_text):
    ''' given a 'new' version of a file and the patch that created it,
    return the 'old' version of the file, by simply applying the patch in reverse
    '''
    diff_tool = dmp()
    patches = diff_tool.patch_fromText(patches_as_text)
    reverse_patches = reverse(patches)
    return diff_tool.patch_apply(reverse_patches, new)[0]


def fix_patch(patch):
    ''' return new patch with fixed unified diff headers.
    For some reason, github returns some headers with a missing EOL, which
    prevents the diff_match_patch regex from matching because it has a $ at its end.
    I played with the Accept header in the request to set the media type to 'diff',
    but it doesn't work.
    Instead, I'm now fixing the patch directly. We just need to add a newline after the
    diff headers.
    '''
    return re_diff_headers.sub(r'\1\n', patch)


