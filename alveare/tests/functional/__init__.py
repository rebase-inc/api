import json
import datetime
import unittest

from alveare import models, create_app
from alveare.common.database import DB
from alveare.common.mock import create_the_world

class AlveareRestTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(DB)
        self.db = DB

        # not really sure why this is required
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        self.db.create_all()
        self.db.session.commit()

        create_the_world(self.db)
        self.db.session.commit()

        self.addCleanup(self.cleanup)

    def cleanup(self):
        self.db.session.remove()
        self.db.drop_all()
        self.db.get_engine(self.app).dispose()
        self.app_context.pop()

    def get_resource(self, url, expected_code=200):
        # the header is required because of flask jsonify
        # see http://stackoverflow.com/questions/16908943/flask-display-json-in-a-neat-way
        response = self.client.get(url, headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, expected_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        return json.loads(response.data.decode('utf-8'))

    def post_resource(self, url, data, expected_code = 201):
        response = self.client.post(url, data = data, headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, expected_code)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        return json.loads(response.data.decode('utf-8'))


