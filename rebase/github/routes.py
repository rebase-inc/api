from flask import redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth

def register_github_routes(app):
    oauth = OAuth(app)
    github = oauth.remote_app(
        'github',
        consumer_key='ccfe7b7be7560c9a112e',
        consumer_secret='1779c1d363dec567c81c01ef266e4d3f30f79a8d',
        request_token_params={'scope': 'user:email'},
        base_url='https://api.github.com/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize'
    )

    @app.route('/github/')
    def index():
        if 'github_token' in session:
            me = github.get('user')
            return jsonify(me.data)
        return redirect(url_for('login'))

    @app.route('/github/login')
    def login():
        return github.authorize(callback=url_for('authorized', _external=True))

    @app.route('/github/logout')
    def logout():
        session.pop('github_token', None)
        return redirect(url_for('index'))

    @app.route('/github/authorized')
    def authorized():
        resp = github.authorized_response()
        app.logger.debug(resp)
        if resp is None:
            return 'Access denied: reason=%s error=%s' % (
                request.args['error'],
                request.args['error_description']
            )
        session['github_token'] = (resp['access_token'], '')
        me = github.get('user')
        return jsonify(me.data)

    @github.tokengetter
    def get_github_oauth_token():
        return session.get('github_token')
