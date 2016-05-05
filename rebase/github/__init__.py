from urllib.parse import urlparse

from flask_oauthlib.client import OAuth


def create_github_apps(app):
    oauth = OAuth(app)
    common_settings = {
            'request_token_params': {'scope': 'user, repo'},
            'base_url': 'https://api.github.com/',
            'request_token_url': None,
            'access_token_method': 'POST',
            'access_token_url': 'https://github.com/login/oauth/access_token',
            'authorize_url': 'https://github.com/login/oauth/authorize'
    }
    return {
        urlparse(app.config['APP_URL']).hostname: oauth.remote_app(
            'app',
            consumer_key=app.config['GITHUB_APP_ID'],
            consumer_secret=app.config['GITHUB_APP_SECRET'],
            **common_settings
        ),
        urlparse(app.config['CODE2RESUME_URL']).hostname: oauth.remote_app(
            'code2resume',
            consumer_key=app.config['GITHUB_CODE2RESUME_ID'],
            consumer_secret=app.config['GITHUB_CODE2RESUME_SECRET'],
            **common_settings
        ),
    }
