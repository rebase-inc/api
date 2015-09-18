from unittest import skip

from . import RebaseRestTestCase, RebaseNoMockRestTestCase
from rebase.common.mock import create_one_user
from rebase.common.utils import RebaseResource, validate_resource_collection
from rebase.tests.common.contractor import (
    case_cleared_contractors,
    case_cleared_contractors_as_contractor,
    case_nominated_contractors,
)
from rebase.models import User


class TestContractorResource(RebaseRestTestCase):
    def setUp(self):
        self.contractor_resource = RebaseResource(self, 'Contractor')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        contractor = self.contractor_resource.get_any()
        self.assertTrue(contractor) # mock should have created at least one acode_clearance_resourceount
        self.assertTrue(contractor['id'])

    def test_remote_work_history(self):
        self.login_admin()
        contractor = self.contractor_resource.get_any()
        rwh_res = RebaseResource(self, 'RemoteWorkHistory')
        response = self.post_resource('remote_work_histories', dict(contractor=contractor))
        new_rwh = response['remote_work_history']
        self.assertEqual(new_rwh['id'], contractor['id'])
        queried_contractor = self.contractor_resource.get(contractor)
        self.contractor_resource.assertComposite(queried_contractor['remote_work_history'], new_rwh)
        rwh_res.delete(**new_rwh)

    def test_code_clearance(self):
        self.login_admin()
        contractor = self.contractor_resource.get_any()
        project = RebaseResource(self, 'Project').get_any()
        code_clearance_resource = RebaseResource(self, 'CodeClearance')
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
        contractor = self.post_resource(
            'contractors',
            dict(
                user={
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            )
        )['contractor']
        self.logout()
        self.login_as_new_user()
        self.delete_resource('contractors/{id}'.format(**contractor), 401)
        self.login(user.email, 'foo')
        self.delete_resource('contractors/{id}'.format(**contractor))

class TestContractor(RebaseNoMockRestTestCase):
    def setUp(self):
        super().setUp()
        self.resource = RebaseResource(self, 'Contractor')

    def test_admin_create(self):
        admin_user = create_one_user(self.db, admin=True)
        other_user = create_one_user(self.db)
        self.login(admin_user.email, 'foo')
        _user = {
            'id': other_user.id,
            'first_name': other_user.first_name,
            'last_name': other_user.last_name
        }
        self.resource.create(
            user=_user
        )

    def test_user_create(self):
        user = create_one_user(self.db)
        logged_user = self.login(user.email, 'foo')
        _user = {
            'id': logged_user['id'],
            'first_name': logged_user['first_name'],
            'last_name': logged_user['last_name']
        }
        self.resource.create(
            user=_user
        )

    def test_get_all_cleared_contractors_as_manager(self):
        mgr_user, expected_resources = self._run(case_cleared_contractors, 'manager')
        validate_resource_collection(self, expected_resources)

    def test_get_all_nominated_contractors_as_manager(self):
        mgr_user, expected_resources = self._run(case_nominated_contractors, 'manager')
        validate_resource_collection(self, expected_resources)

    def test_get_all_contractors_as_contractor(self):
        contractor_user, expected_resources = self._run(case_cleared_contractors_as_contractor, 'contractor')
        validate_resource_collection(self, expected_resources)

    def test_manager_cannot_modify_contractor(self):
        mgr_user, expected_contractors = self._run(case_cleared_contractors, 'contractor')
        contractor = expected_contractors[0]
        contractor_blob = self.resource.get(contractor.id)
        self.assertTrue(contractor_blob)
        self.resource.delete(expected_status=401, **contractor_blob) # test DELETE 
        self.resource.update(expected_status=401, **contractor_blob) # test PUT

    def test_contractor_cannot_modify_another_contractor(self):
        contractor_user, expected_resources = self._run(case_cleared_contractors_as_contractor, 'contractor')
        other_contractor = self.resource.get(expected_resources[1].id)
        self.resource.update(expected_status=401, **other_contractor)
        self.resource.delete(expected_status=401, **other_contractor)

    def test_contractor_can_modify_or_delete_self(self):
        contractor_user, expected_resources = self._run(case_cleared_contractors_as_contractor, 'contractor')
        contractor = contractor_user.roles.all()[0]
        contractor_blob = self.resource.get(contractor.id)
        new_busyness = 123456
        contractor_blob['busyness'] = new_busyness
        self.assertEqual(self.resource.update(**contractor_blob)['busyness'], new_busyness)
        self.resource.delete(**contractor_blob)

    def test_anonymous_cannot_view_or_modify_contractor(self):
        contractor_user, expected_resources = self._run(case_cleared_contractors_as_contractor, 'manager')
        contractor = contractor_user.roles.all()[0]
        self.logout()
        contractor_blob = self.resource.get(contractor.id, 401)
        self.resource.update(expected_status=401, **{'id': contractor.id})
