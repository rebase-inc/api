from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip


class TestContractorResource(AlveareRestTestCase):
    def setUp(self):
        self.contractor_resource = AlveareResource(self, 'Contractor')
        super().setUp()

    def test_get_one(self):
        contractor = self.contractor_resource.get_any()
        self.assertTrue(contractor) # mock should have created at least one account
        self.assertTrue(contractor['id'])

    def test_remote_work_history(self):
        contractor = self.contractor_resource.get_any()
        rwh_res = AlveareResource(self, 'RemoteWorkHistory')
        new_rwh = rwh_res.create(
            id=contractor['id']
        )
        queried_contractor = self.contractor_resource.get(contractor)
        self.contractor_resource.assertComposite(queried_contractor['remote_work_history'], new_rwh)
        rwh_res.delete(new_rwh)

    def test_code_clearance(self):
        contractor = self.contractor_resource.get_any()
        project = AlveareResource(self, 'Project').get_any()
        cc = AlveareResource(self, 'CodeClearance')
        code_clearance = cc.create(
            pre_approved =   True,
            project = {'id': project['id']},
            contractor = {'id': contractor['id']}
        )
        queried_contractor = self.contractor_resource.get(contractor)
        for clearance in queried_contractor['clearances']:
            if clearance['id'] == code_clearance['id']:
                self.contractor_resource.assertComposite(clearance, code_clearance)

        # now delete all clearances
        for clearance in queried_contractor['clearances']:
            cc.delete(clearance)
        self.assertFalse(self.contractor_resource.get(contractor)['clearances'])

    def test_create(self):
        user_resource = AlveareResource(self, 'User')
        user = user_resource.just_ids(user_resource.get_any())
        self.contractor_resource.create(user=user)

    def test_update(self):
        contractor = self.contractor_resource.get_any()
        contractor['busyness'] = 123
        #contractor = dict(id = contractor['id'], busyness = 4)
        #raise Exception(contractor)
        self.contractor_resource.update(**contractor)

    def test_delete(self):
        self.contractor_resource.delete_any()

    def test_delete_user(self):
        contractor = self.contractor_resource.get_any()
        self.delete_resource('users/{}'.format(contractor['user']['id']))
        self.get_resource(self.contractor_resource.url(contractor), 404)
