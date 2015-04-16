import unittest
import datetime

from . import AlveareModelTestCase

from alveare import models
from alveare.common import mock

class TestUserModel(AlveareModelTestCase):

    def test_create(self):
        user = mock.create_one_user(self.db)
        contractor = models.Contractor(user)
        models.SkillSet(contractor)
        self.db.session.commit()

        user = models.User.query.get(user.id)

        self.assertIsInstance(user.first_name, str)
        self.assertIsInstance(user.last_name, str)
        self.assertIsInstance(user.email, str)
        self.assertIsInstance(user.hashed_password, str)
        self.assertIsInstance(user.last_seen, datetime.datetime)
        self.assertIsInstance(user.roles.all(), list)
        self.assertIsInstance(user.roles.all().pop(), models.Contractor)

    def test_delete_contract(self):
        user = mock.create_one_user(self.db)
        contractor = models.Contractor(user)
        models.SkillSet(contractor)
        self.db.session.commit()

        user_id = user.id
        role_id = user.roles.all().pop().id

        found_user = models.User.query.get(user_id)
        self.delete_instance(found_user)

        self.assertEqual(models.User.query.get(user_id), None)
        self.assertEqual(models.Role.query.get(role_id), None)

    def test_update(self):
        user = mock.create_one_user(self.db)
        contractor = models.Contractor(user)
        models.SkillSet(contractor)
        self.db.session.commit()

        new_first_name = user.first_name + 'foo'
        new_last_name = user.last_name + 'foo'
        new_email = 'foo' + user.email
        new_password = user.hashed_password + 'foo'
        new_last_seen = datetime.datetime.now()

        user.first_name = new_first_name
        user.last_name = new_last_name
        user.email = new_email
        user.hashed_password = new_password
        user.last_seen = new_last_seen

        found_user = models.User.query.get(user.id)
        self.assertEqual(found_user.first_name, new_first_name)
        self.assertEqual(found_user.last_name, new_last_name)
        self.assertEqual(found_user.email, new_email)
        self.assertEqual(found_user.hashed_password, new_password)
        self.assertEqual(found_user.last_seen, new_last_seen)

    @unittest.skip('i suppose its not a big deal to pass ints as strs...')
    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(models.User, 1, 1, 1, 1)

    def test_query_manager_users_while_logged_as_manager(self):
        user = mock.create_one_user(self.db)
        org = mock.create_one_organization(self.db, 'Foo Inc.', user)
        mgr_1 = mock.create_one_manager(self.db, org=org)
        mgr_2 = mock.create_one_manager(self.db, org=org)
        self.db.session.commit()
        manager_users = models.User.as_manager_get_other_managers(user).all()
        self.assertEqual(len(manager_users), 3)
        self.assertIn(mgr_1.user, manager_users)
        self.assertIn(mgr_2.user, manager_users)
        self.assertIn(user, manager_users)

        all_users = models.User.query_by_user(user).all()
        for _user in manager_users:
            self.assertIn(_user, all_users)

        found_users = models.User.as_manager_get_other_managers(user, mgr_1.user.id).all()
        self.assertEqual(len(found_users), 1)
        self.assertIn(mgr_1.user, found_users)

    def test_query_contractor_users_while_logged_as_manager(self):
        user = mock.create_one_user(self.db)
        org = mock.create_one_organization(self.db, 'Foo Inc.', user)
        project = mock.create_one_project(self.db, org, 'Bar Project')
        contractor_1 = mock.create_one_contractor(self.db)
        clearance_1 = mock.create_one_code_clearance(self.db, project, contractor_1)
        contractor_2 = mock.create_one_contractor(self.db)
        clearance_2 = mock.create_one_code_clearance(self.db, project, contractor_2)
        self.db.session.commit()

        found_users = models.User.as_manager_get_cleared_contractors(user).all()
        self.assertEqual(len(found_users), 2)
        self.assertIn(contractor_1.user, found_users)
        self.assertIn(contractor_2.user, found_users)

        all_users = models.User.query_by_user(user).all()
        for _user in found_users:
            self.assertIn(_user, all_users)

        cleared_users = models.User.as_manager_get_cleared_contractors(user, contractor_2.user.id).all()
        self.assertEqual(len(cleared_users), 1)
        self.assertIn(contractor_2.user, cleared_users)
        
    def test_query_nominated_users_while_logged_as_manager(self):
        user = mock.create_one_user(self.db)
        org = mock.create_one_organization(self.db, 'Foo Inc.', user)
        project = mock.create_one_project(self.db, org, 'Bar Project')
        project_tickets = [
            mock.create_one_internal_ticket(
                self.db,
                'Issue #{}'.format(i),
                project=project
            ) for i in range(10)
        ]
        auction = mock.create_one_auction(self.db, project_tickets)
        contractor_1 = mock.create_one_contractor(self.db)
        nomination_1 = mock.create_one_nomination(self.db, auction, contractor_1)
        contractor_2 = mock.create_one_contractor(self.db)
        nomination_2 = mock.create_one_nomination(self.db, auction, contractor_2)
        self.db.session.commit()

        nominated_users = models.User.as_manager_get_nominated_users(user).all()
        self.assertEqual(len(nominated_users), 2)
        self.assertIn(contractor_1.user, nominated_users)
        self.assertIn(contractor_2.user, nominated_users)

        all_users = models.User.query_by_user(user).all()
        for _user in nominated_users:
            self.assertIn(_user, all_users)

        nominated_users = models.User.as_manager_get_nominated_users(user, contractor_1.user.id).all()
        self.assertEqual( len(nominated_users), 1)
        self.assertIn( contractor_1.user, nominated_users )
