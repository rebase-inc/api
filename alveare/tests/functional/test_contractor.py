from . import AlveareRestTestCase
from alveare.common.resource import AlveareResource
from unittest import skip


class TestContractorResource(AlveareRestTestCase):
    def setUp(self):
        self.r = AlveareResource(self, 'Contractor')
        super().setUp()

    def test_get_one(self):
        contractor = self.r.get_any()
        self.assertTrue(contractor) # mock should have created at least one account
        self.assertTrue(contractor['id'])

    def test_remote_work_history(self):
        contractor = self.r.get_any()
        rwh_res = AlveareResource(self, 'RemoteWorkHistory')
        new_rwh = rwh_res.create(
            id=contractor['id']
        )
        queried_contractor = self.r.get(contractor)
        self.r.is_in(queried_contractor['remote_work_history'], new_rwh)
        rwh_res.delete(new_rwh)

    def test_code_clearance(self):
        contractor = self.r.get_any()
        project = AlveareResource(self, 'Project').get_any()
        cc = AlveareResource(self, 'CodeClearance')
        code_clearance = cc.create(
            pre_approved =   True,
            project = {'id': project['id']},
            contractor = {'id': contractor['id']}
        )
        queried_contractor = self.r.get(contractor)
        for clearance in queried_contractor['clearances']:
            if clearance['id'] == code_clearance['id']:
                self.r.is_in(clearance, code_clearance)

        # now delete all clearances
        for clearance in queried_contractor['clearances']:
            cc.delete(clearance)
        self.assertFalse(self.r.get(contractor)['clearances'])

    def test_create(self):
        user = AlveareResource(self, 'User').get_any()
        user.pop('last_seen')
        user.pop('email')
        self.r.create(user=user)

    def test_update(self):
        contractor = self.r.get_any()
        contractor['busyness'] = 123
        #contractor = dict(id = contractor['id'], busyness = 4)
        #raise Exception(contractor)
        self.r.update(**contractor)

    def test_delete(self):
        self.r.delete_any()

    def test_delete_user(self):
        contractor = self.r.get_any()
        self.delete_resource('users/{}'.format(contractor['user']['id']))
        self.get_resource(self.r.url(contractor), 404)
