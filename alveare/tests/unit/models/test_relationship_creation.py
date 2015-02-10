""" This is a set of tests designed to help a user understand sqlalchemy relationships """
import unittest
from sqlalchemy.exc import NoForeignKeysError

from . import AlveareModelTestCase

from alveare.common.database import DB

class TestFullyDefinedRelationship(AlveareModelTestCase):

    def setUp(self):
        class User1(DB.Model):
            id = DB.Column(DB.Integer, primary_key=True)
            name = DB.Column(DB.String)
            addresses = DB.relationship("Address1", backref="user")
        class Address1(DB.Model):
            id = DB.Column(DB.Integer, primary_key=True)
            email = DB.Column(DB.String)
            user_id = DB.Column(DB.Integer, DB.ForeignKey('user1.id'))
        self.User = User1
        self.Address = Address1
        super(TestFullyDefinedRelationship, self).setUp()

    def test_add_and_remove_address(self):
        u1 = self.User()
        a1 = self.Address()
        self.assertEqual(len(u1.addresses), 0)
        u1.addresses.append(a1)
        self.assertEqual(len(u1.addresses), 1)
        self.assertNotEqual(a1.user, None)
        a1.user = None
        self.assertEqual(len(u1.addresses), 0)

class TestMissingForeignKeyRelationship(AlveareModelTestCase):

    def setUp(self):
        class User2(DB.Model):
            id = DB.Column(DB.Integer, primary_key=True)
            name = DB.Column(DB.String)
            addresses = DB.relationship("Address2", backref="user")
        class Address2(DB.Model):
            id = DB.Column(DB.Integer, primary_key=True)
            email = DB.Column(DB.String)
        self.User = User2
        self.Address = Address2
        super(TestMissingForeignKeyRelationship, self).setUp()

    def test_add_and_remove_address(self):
        with self.assertRaises(NoForeignKeysError):
            u1 = self.User()

class TestMissingBackref(AlveareModelTestCase):

    def setUp(self):
        class User3(DB.Model):
            id = DB.Column(DB.Integer, primary_key=True)
            name = DB.Column(DB.String)
            addresses = DB.relationship("Address3")
        class Address3(DB.Model):
            id = DB.Column(DB.Integer, primary_key=True)
            email = DB.Column(DB.String)
            user_id = DB.Column(DB.Integer, DB.ForeignKey('user3.id'))
        self.User = User3
        self.Address = Address3
        super(TestMissingBackref, self).setUp()

    def test_add_and_remove_address(self):
        u1 = self.User()
        a1 = self.Address()
        self.db.session.add(u1)
        self.db.session.add(a1)
        self.db.session.commit()
        self.assertEqual(len(u1.addresses), 0)
        u1.addresses.append(a1)
        self.db.session.commit()
        self.assertEqual(len(u1.addresses), 1)
        self.assertEqual(u1.id, a1.user_id)
