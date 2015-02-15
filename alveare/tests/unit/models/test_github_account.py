import unittest

from . import AlveareModelTestCase
from alveare.models import Contractor, RemoteWorkHistory, GithubAccount
from alveare.common.mock import create_one_github_account, create_one_remote_work_history

class TestGithubAccountModel(AlveareModelTestCase):

    def test_create(self):
        github_account = create_one_github_account(self.db)
        self.db.session.commit()

        self.assertNotEqual( Contractor.query.all(),        [])
        self.assertNotEqual( RemoteWorkHistory.query.all(), [])
        self.assertNotEqual( GithubAccount.query.all(),     [])

    def test_delete(self):
        github_account = create_one_github_account(self.db)
        rwh = github_account.remote_work_history

        total = 25
        for i in range(25):
            GithubAccount(rwh, '#{}'.format(i))

        total += 1 # accounting for the first one created

        self.assertEqual( len(rwh.github_accounts), total)
        self.db.session.commit()
        self.delete_instance(github_account)
        total -= 1

        self.assertEqual( len(GithubAccount.query.all()), total)

        self.assertNotEqual( RemoteWorkHistory.query.all(), [])
        self.assertNotEqual( Contractor.query.all(), [])

        rwh = RemoteWorkHistory.query.all()[0]
        rwh.github_accounts.clear()
        self.db.session.commit()
        self.assertEqual(GithubAccount.query.all(), [])

    def test_delete_parent(self):
        rwh = create_one_remote_work_history(self.db)
        for i in range(25):
            GithubAccount(rwh, '#{}'.format(i))
        self.db.session.commit()
        self.assertEqual(len(GithubAccount.query.all()), 25)
        self.delete_instance(rwh)

        self.assertNotEqual(   Contractor.query.all(),          []) # contractor still there
        self.assertEqual(      RemoteWorkHistory.query.all(),   []) # but not its work history
        self.assertEqual(      GithubAccount.query.all(),       []) # and its accounts

    def test_delete_orphan(self):
        gh_account = create_one_github_account(self.db)
        self.db.session.commit()
        rwh = RemoteWorkHistory.query.all()[0]
        self.assertNotEqual( rwh, [])

        # unrelate (not a direct delete!) gh_account from rwh
        rwh.github_accounts.clear()
        self.db.session.commit()

        # delete-orphan should have deleted gh_account after the commit is done

        self.db.session.commit()
        self.db.session.close() # clear all cached instances

        self.assertEqual( GithubAccount.query.all(), [])


    def test_bad_create(self):
        gh = create_one_github_account(self.db)
        self.db.session.commit()
        with self.assertRaises(KeyError):
            foo_bar = GithubAccount(gh, 'bar')
        with self.assertRaises(AttributeError):
            foo_bar2 = GithubAccount('foo', 'bar')
