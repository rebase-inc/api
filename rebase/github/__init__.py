from flask_oauthlib.client import OAuth


def create_github_app(app):
    oauth = OAuth(app)
    return oauth.remote_app(
        'github',
        consumer_key=app.config['GITHUB_CLIENT_ID'],
        consumer_secret=app.config['GITHUB_CLIENT_SECRET'],
        request_token_params={'scope': 'user, repo'},
        base_url='https://api.github.com/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize'
    )
