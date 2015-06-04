from unittest import skip

from . import AlveareRestTestCase, AlveareNoMockRestTestCase
from alveare.common.utils import AlveareResource, validate_resource_collection
from alveare.tests.common.contractor import (
    case_cleared_contractors,
    case_cleared_contractors_as_contractor,
    case_nominated_contractors,
)
from alveare.models import User


class TestContractorResource(AlveareRestTestCase):
    def setUp(self):
        self.contractor_resource = AlveareResource(self, 'Contractor')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        contractor = self.contractor_resource.get_any()
        self.assertTrue(contractor) # mock should have created at least one acode_clearance_resourceount
        self.assertTrue(contractor['id'])

    def test_remote_work_history(self):
        self.login_admin()
        contractor = self.contractor_resource.get_any()
        rwh_res = AlveareResource(self, 'RemoteWorkHistory')
        response = self.post_resource('remote_work_histories', dict(contractor=contractor))
        new_rwh = response['remote_work_history']
        self.assertEqual(new_rwh['id'], contractor['id'])
        queried_contractor = self.contractor_resource.get(contractor)
        self.contractor_resource.assertComposite(queried_contractor['remote_work_history'], new_rwh)
        rwh_res.delete(**new_rwh)

    def test_code_clearance(self):
        self.login_admin()
        contractor = self.contractor_resource.get_any()
        project = AlveareResource(self, 'Project').get_any()
        code_clearance_resource = AlveareResource(self, 'CodeClearance')
        code_clearance = code_clearance_resource.create(
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
            code_clearance_resource.delete(**clearance)
        self.assertFalse(self.contractor_resource.get(contractor)['clearances'])

    def test_create(self):
        self.login_admin()
        user_resource = AlveareResource(self, 'User')
        user = user_resource.just_ids(user_resource.get_any())
        self.contractor_resource.create(user=user)

    def test_update(self):
        self.login_admin()
        contractor = self.contractor_resource.get_any()
        contractor['busyness'] = 123
        self.contractor_resource.update(**contractor)

    def test_delete(self):
        self.login_admin()
        self.contractor_resource.delete_any()

    def test_delete_user(self):
        self.login_admin()
        contractor = self.contractor_resource.get_any()
        self.delete_resource('users/{}'.format(contractor['user']['id']))
        self.get_resource(self.contractor_resource.url(contractor), 404)

    def test_that_only_the_user_can_delete(self):
        user = User('foo', 'bar', 'foo@bar.com', 'foo')
        self.db.session.add(user)
        self.db.session.commit()
        self.login(user.email, 'foo')
        contractor = self.post_resource('contractors', dict(user={'id': user.id}))['contractor']
        self.logout()
        self.login_as_new_user()
        self.delete_resource('contractors/{id}'.format(**contractor), 401)
        self.login(user.email, 'foo')
        self.delete_resource('contractors/{id}'.format(**contractor))

class TestContractorNoMock(AlveareNoMockRestTestCase):
    def setUp(self):
        super().setUp()
        self.resource = AlveareResource(self, 'Contractor')

    def test_get_all_cleared_contractors_as_manager(self):
        mgr_user, expected_resources = case_cleared_contractors(self.db)
        validate_resource_collection(self, mgr_user, expected_resources)

    def test_get_all_nominated_contractors_as_manager(self):
        mgr_user, expected_resources = case_nominated_contractors(self.db)
        validate_resource_collection(self, mgr_user, expected_resources)

    def test_get_all_contractors_as_contractor(self):
        contractor, expected_resources = case_cleared_contractors_as_contractor(self.db)
        validate_resource_collection(self, contractor.user, expected_resources)

    def test_manager_cannot_modify_contractor(self):
        mgr_user, expected_contractors = case_cleared_contractors(self.db)
        self.login(mgr_user.email, 'foo')
        contractor = expected_contractors[0]
        contractor_blob = self.resource.get(contractor.id)
        self.assertTrue(contractor_blob)
        self.resource.delete(expected_status=401, **contractor_blob) # test DELETE 
        self.resource.update(expected_status=401, **contractor_blob) # test PUT

    def test_contractor_cannot_modify_another_contractor(self):
        contractor, expected_resources = case_cleared_contractors_as_contractor(self.db)
        self.login(contractor.user.email, 'foo')
        other_contractor = self.resource.get(expected_resources[1].id)
        self.resource.update(expected_status=401, **other_contractor)
        self.resource.delete(expected_status=401, **other_contractor)

    def test_contractor_can_modify_or_delete_self(self):
        contractor, expected_resources = case_cleared_contractors_as_contractor(self.db)
        self.login(contractor.user.email, 'foo')
        contractor_blob = self.resource.get(contractor.id)
        new_busyness = 123456
        contractor_blob['busyness'] = new_busyness
        self.assertEqual(self.resource.update(**contractor_blob)['busyness'], new_busyness)
        self.resource.delete(**contractor_blob)

    def test_anonymous_cannot_view_or_modify_contractor(self):
        contractor, expected_resources = case_cleared_contractors_as_contractor(self.db)
        self.logout()
        contractor_blob = self.resource.get(contractor.id, 401)
        self.resource.update(expected_status=401, **{'id': contractor.id})
