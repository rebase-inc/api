from flask import request

def setup_cors(app):
    @app.after_request
    def add_cors(resp):
        """ Ensure all responses have the CORS headers. This ensures any failures are also accessible
        by the client. """
        resp.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin','*')
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        resp.headers['Access-Control-Allow-Methods'] = 'PUT, POST, OPTIONS, GET'
        resp.headers['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', 'Authorization' )
        # set low for debugging
        if app.debug:
            resp.headers['Access-Control-Max-Age'] = '1000'
        return resp
